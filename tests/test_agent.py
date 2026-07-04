from askdata.agent import AskDataAgent
from askdata.config import Settings
from askdata.llm import ScriptedClient

GOOD_SQL = "```sql\nSELECT count(*) AS n_orders FROM orders\n```"
BAD_SQL = "```sql\nSELECT profit_margin FROM orders\n```"
PASS = '{"verdict": "pass", "reason": "ok"}'
FAIL = '{"verdict": "fail", "reason": "does not answer the question"}'


def make_agent(db_path, responses, verify=True):
    return AskDataAgent(
        db_path=str(db_path),
        llm=ScriptedClient(responses),
        settings=Settings(max_attempts=3),
        verify=verify,
    )


def test_trusted_first_try(db_path):
    agent = make_agent(db_path, [GOOD_SQL, PASS, "There are 1,200 orders."])
    ans = agent.ask("How many orders are there?")
    assert ans.status == "trusted"
    assert ans.attempts == 1
    assert ans.df.iloc[0, 0] == 1200
    assert "1,200" in ans.text


def test_repaired_after_bad_identifier(db_path):
    # attempt 1 fails static identifier check (no LLM judge call), attempt 2 passes
    agent = make_agent(db_path, [BAD_SQL, GOOD_SQL, PASS, "1,200 orders."])
    ans = agent.ask("How many orders are there?")
    assert ans.status == "repaired"
    assert ans.attempts == 2


def test_abstains_when_model_declines(db_path):
    agent = make_agent(db_path, ["ABSTAIN — there is no cost data in this schema."])
    ans = agent.ask("What is the profit margin?")
    assert ans.status == "abstained"
    assert "cost data" in ans.text


def test_abstains_after_repeated_judge_failures(db_path):
    agent = make_agent(db_path, [GOOD_SQL, FAIL, GOOD_SQL, FAIL, GOOD_SQL, FAIL])
    ans = agent.ask("Something the judge never accepts")
    assert ans.status == "abstained"
    assert ans.attempts == 3


def test_separate_judge_client(db_path):
    gen = ScriptedClient([GOOD_SQL, "1,200 orders."])
    judge = ScriptedClient([PASS])
    agent = AskDataAgent(
        db_path=str(db_path), llm=gen, judge_llm=judge, settings=Settings(max_attempts=3)
    )
    ans = agent.ask("How many orders are there?")
    assert ans.status == "trusted"
    assert len(judge.calls) == 1  # the judge ran on its own client
    assert len(gen.calls) == 2    # generation + summary stayed on the generator


def test_baseline_skips_verification(db_path):
    # no judge/summary-judge responses needed beyond generation + summary
    agent = make_agent(db_path, [GOOD_SQL, "1,200 orders."], verify=False)
    ans = agent.ask("How many orders are there?")
    assert ans.status == "trusted"
    assert ans.checks == []
