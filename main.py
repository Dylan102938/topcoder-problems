from topcoder_problems.generator import create_problem_files
from topcoder_problems.scraper import TopCoderScraper

scraper = TopCoderScraper()
problems = scraper.run()

for i in range(20):
    create_problem_files(problems[i])