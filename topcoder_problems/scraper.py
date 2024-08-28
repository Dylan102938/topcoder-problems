import os
from typing import List, Optional

import requests
from bs4 import BeautifulSoup as bs

from topcoder_problems.types import (TopCoderDivision, TopCoderProblem,
                                     TopCoderScraperConfig, TopCoderType)

from .utils import PROJECT_ROOT, FileSystemCache


def extract_problem_metadata(problem_row, base_url: Optional[str]=None):
    cells = problem_row.find_all('td')
    assert len(cells) == 10, f"Expected 10 cells per row, got {len(cells)}"

    return {
        "name": cells[0].text.strip(),
        "link": f"{base_url}{cells[0].find('a').get('href')}" if base_url else cells[0].find('a').get('href'),
        "challenge": cells[1].text.strip(),
        "date": cells[2].text.strip(),
        "writer": cells[3].text.strip(),
        "div_1_level": int(cells[5].text.strip()) if cells[5].text.strip() else None,
        "div_2_level": int(cells[7].text.strip()) if cells[7].text.strip() else None,
    }


def is_right_division(problem, divisions: List[TopCoderDivision]):
    if not divisions:
        return True

    for division in divisions:
        if division["division_id"] == 1 and problem["div_1_level"] in division["levels"]:
            return True
        
        if division["division_id"] == 2 and problem["div_2_level"] in division["levels"]:
            return True
    
    return False


class TopCoderScraper:
    _DEFAULT_CONFIG: TopCoderScraperConfig = {
        "divisions": None,
        "generate_tests": True,
        "url": "https://archive.topcoder.com",
        "limit": 50,
        "page": 0
    }

    _DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self, config: Optional[TopCoderScraperConfig]=None):
        self.config = {
            **self._DEFAULT_CONFIG,
            **config
        } if config else self._DEFAULT_CONFIG

    def run(self, with_cache=True, cache_dir: Optional[str]=None) -> List[TopCoderProblem]:
        if with_cache and not cache_dir:
            cache_dir = os.path.join(PROJECT_ROOT, "cache/")

        problems_index = self._load_problem_index(with_cache, cache_dir)
        
        skipped, count = 0, 0
        problems = []

        for problem in problems_index:
            if is_right_division(problem, self.config["divisions"]):
                if count >= self.config["limit"]:
                    break

                if skipped < self.config["limit"] * self.config["page"]:
                    skipped += 1
                    continue
                
                problems.append(self._get_problem(problem["link"], with_cache, cache_dir))
                count += 1
        
        return problems
    
    def _load_problem_index(self, with_cache: bool, cache_dir: str):
        if with_cache:
            cache = FileSystemCache(os.path.join(cache_dir, "problems_index.pkl"))
            problems_index = cache(self._fetch_problem_index_no_cache)
        else:
            problems_index = self._fetch_problem_index_no_cache()

        return problems_index

    def _fetch_problem_index_no_cache(self):
        response = requests.get(f"{self.config['url']}/ProblemArchive", headers=self._DEFAULT_HEADERS)

        if not response.ok:
            raise Exception(f"Failed to fetch page: {response.status_code}")

        soup = bs(response.text, "html.parser")

        table = soup.find("table")
        rows = [extract_problem_metadata(problem, base_url=self.config["url"]) for problem in table.find_all('tr')[1:]]

        return rows

    def _get_problem(self, problem_url: str, with_cache: bool, cache_dir: str):
        if with_cache:
            clean_url_path = problem_url.split("/")[-1].split("?")[0]
            cache = FileSystemCache(os.path.join(cache_dir, f"{clean_url_path}.pkl"))
            problem = cache(self._get_problem_no_cache, problem_url)
        else:
            problem = self._fetch_problem_index_no_cache(problem_url)
        
        return problem

    def _get_problem_no_cache(self, problem_url: str) -> TopCoderProblem:
        response = requests.get(problem_url, headers=self._DEFAULT_HEADERS)
        
        if not response.ok:
            raise Exception(f"Failed to fetch page: {response.status_code}")
        
        soup = bs(response.text, "html.parser")

        description = soup.find('h3', text='Problem Statement').find_next('div').text.strip()
        
        definition = soup.find('h3', text='Definition')
        method_name = definition.find_next('dt', text='Method:').find_next('dd').text.strip()
        return_type = definition.find_next('dt', text='Returns:').find_next('dd').text.strip()
        method_signature = definition.find_next('dt', text='Method signature:').find_next('dd').text
        signature_parts = method_signature.split('(')
        parameters_text = signature_parts[1].strip(')')
        parameters = [param.strip() for param in parameters_text.split(',')]

        examples = soup.find('h3', text='Examples').find_all_next('li')
        test_cases = []

        for example in examples:
            inputs = []
            output = None
            for p in example.find_all('p'):
                text = p.text.strip()
                if not text.startswith('Returns:'):
                    inputs.append(text)
                else:
                    output = text.replace('Returns:', '').strip()
                    break
            
            if len(inputs) > 0 and output is not None:
                test_cases.append({
                    "inputs": inputs,
                    "output": output
                })

        return {
            "id": problem_url.split("/")[-1].split("?")[0],
            "description": description,
            "func_name": method_name,
            "parameters": [
                {
                    "name": param.split()[1],
                    "type": TopCoderType.from_string(param.split()[0])
                } for param in parameters if param.strip() != ""
            ],
            "return_type": TopCoderType.from_string(return_type),
            "test_cases": test_cases
        }


