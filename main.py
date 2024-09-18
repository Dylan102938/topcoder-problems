from topcoder_problems.generator import create_problem_files
from topcoder_problems.scraper import TopCoderScraper

scraper = TopCoderScraper({
    "divisions": [{
        "division_id": 1,
        "levels": [2]
    }],
    "limit": 10,
    "page": 1
})

# problems = scraper.run()

# for problem in problems:
#     create_problem_files(problem)

problem = scraper._get_problem("https://archive.topcoder.com/ProblemStatement/pm/1614", with_cache=True, cache_dir="./problems")
create_problem_files(problem)