# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
class ParsingError(Exception):
    pass



class BulkParser(object):
    def parse(self, text):
        data = []
        state = self.begin

        lines = text.splitlines()
        error = False

        for line in lines:
            line = line.strip()
            if line:
                try:
                    state = state(line.lower(), line, data)
                except ParsingError as e:
                    if not data:
                        data.append({})
                    data[-1]["error"] = str(e)
                    error = True
                    break

        if not error and not state.expect_end:
            if not data:
                data.append({})
            data[-1]["error"] = (
                "Unexpected end of input, looking for %s"
                % " or ".join(repr(k.title()) for k in state.keys)
                )

        return data


    def begin(self, lc, orig, data):
        if lc.startswith("test that "):
            data.append({"name": orig})
            return self.description
        raise ParsingError("Expected 'Test that ...', not '%s'" % orig)
    begin.keys = ["Test that "]
    begin.expect_end = False


    def description(self, lc, orig, data):
        if lc.startswith("when ") or lc.startswith("and when "):
            if "description" not in data[-1]:
                raise ParsingError(
                    "Expected at least one line of description before '%s'"
                    % orig)
            data[-1]["steps"] = [{"instruction": [orig]}]
            return self.instruction
        data[-1].setdefault("description", []).append(orig)
        return self.description
    description.keys = ["when ", "and when "]
    description.expect_end = False


    def instruction(self, lc, orig, data):
        if lc.startswith("then "):
            data[-1]["steps"][-1]["expectedResult"] = [orig]
            return self.expectedresult
        data[-1]["steps"][-1]["instruction"].append(orig)
        return self.instruction
    instruction.keys = ["then "]
    instruction.expect_end = False


    def expectedresult(self, lc, orig, data):
        if lc == "and":
            self._orig_and = orig
            return self.after_and
        if lc.startswith("test that "):
            data.append({"name": orig})
            return self.description
        if lc.startswith("when ") or lc.startswith("and when "):
            data[-1]["steps"].append({"instruction": [orig]})
            return self.instruction
        data[-1]["steps"][-1]["expectedResult"].append(orig)
        return self.expectedresult
    expectedresult.keys = ["test that ", "when "]
    expectedresult.expect_end = True


    def after_and(self, lc, orig, data):
        if lc.startswith("when "):
            data[-1]["steps"].append({"instruction": [orig]})
            return self.instruction
        data[-1]["steps"][-1]["expectedResult"].extend([self._orig_and, orig])
        return self.expectedresult
    after_and.keys = ["when "]
    after_and.expect_end = False
