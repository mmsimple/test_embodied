import csv
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_robot_log import (
    analyze_log,
    build_defect_candidate_rows,
    parse_log_line,
    write_defect_candidates_csv,
)


class TestAnalyzeRobotLog(unittest.TestCase):
    def test_parse_valid_log_line(self):
        entry = parse_log_line(
            "2026-05-20 09:00:05.883 [ERROR] [control] motor timeout"
        )

        self.assertEqual(entry["time"], "2026-05-20 09:00:05.883")
        self.assertEqual(entry["level"], "ERROR")
        self.assertEqual(entry["module"], "control")
        self.assertEqual(entry["message"], "motor timeout")

    def test_parse_invalid_log_line(self):
        self.assertIsNone(parse_log_line("bad log line"))

    def test_fail_when_severe_error_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "robot.log"
            log_path.write_text(
                "\n".join(
                    [
                        "2026-05-20 09:00:01.000 [INFO] [system] started",
                        "2026-05-20 09:00:02.000 [ERROR] [control] motor timeout",
                    ]
                ),
                encoding="utf-8",
            )

            analysis = analyze_log(log_path)

        self.assertEqual(analysis["result"], "FAIL")
        self.assertEqual(analysis["severe_count"], 1)
        self.assertEqual(analysis["timeout_count"], 1)

    def test_risk_when_warn_count_greater_than_five(self):
        lines = [
            "2026-05-20 09:00:01.000 [INFO] [system] started",
        ]
        for index in range(6):
            lines.append(
                f"2026-05-20 09:00:0{index + 2}.000 [WARN] [nav] replan triggered"
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "robot.log"
            log_path.write_text("\n".join(lines), encoding="utf-8")
            analysis = analyze_log(log_path)

        self.assertEqual(analysis["result"], "RISK")
        self.assertEqual(analysis["warn_count"], 6)

    def test_risk_when_timeout_count_is_three(self):
        lines = [
            "2026-05-20 09:00:01.000 [WARN] [control] motor timeout",
            "2026-05-20 09:00:02.000 [WARN] [camera] frame timeout",
            "2026-05-20 09:00:03.000 [WARN] [task] service timeout",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "robot.log"
            log_path.write_text("\n".join(lines), encoding="utf-8")
            analysis = analyze_log(log_path)

        self.assertEqual(analysis["result"], "RISK")
        self.assertEqual(analysis["timeout_count"], 3)

    def test_build_defect_candidate_rows_with_priority_and_suggestion(self):
        rows = build_defect_candidate_rows(
            Counter(
                {
                    ("control", "motor timeout"): 2,
                    ("nav", "recovery behavior failed"): 1,
                }
            )
        )

        self.assertEqual(rows[0]["priority"], "P1")
        self.assertEqual(rows[0]["suggestion"], "优先建 Bug 并补充复现材料")
        self.assertEqual(rows[1]["priority"], "P2")
        self.assertEqual(rows[1]["suggestion"], "观察是否复现，必要时合并到相关 Bug")

    def test_write_defect_candidates_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "defects.csv"
            write_defect_candidates_csv(
                Counter({("control", "motor timeout"): 2}),
                csv_path,
            )

            with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(rows[0]["title"], "[control] motor timeout")
        self.assertEqual(rows[0]["priority"], "P1")
        self.assertEqual(rows[0]["suggestion"], "优先建 Bug 并补充复现材料")


if __name__ == "__main__":
    unittest.main()
