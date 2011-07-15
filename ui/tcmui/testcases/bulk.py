class ParsingError(Exception):
    pass



class BulkParser(object):
    def parse(self, text):
        data = []
        state = self.begin

        lines = text.splitlines()

        for line in lines:
            line = line.strip()
            if line:
                try:
                    state = state(line.lower(), line, data)
                except ParsingError as e:
                    if not data:
                        data.append({})
                    data[-1]["error"] = str(e)
                    break

        return data


    def begin(self, lc, orig, data):
        if lc.startswith("test that "):
            data.append({"name": orig})
            return self.description
        raise ParsingError("Expected 'Test that ...', not %r" % orig)


    def description(self, lc, orig, data):
        if lc.startswith("when ") or lc.startswith("and when "):
            if "description" not in data[-1]:
                raise ParsingError(
                    "Expected at least one line of description before %r"
                    % orig)
            data[-1]["steps"] = [{"instruction": [orig]}]
            return self.instruction
        data[-1].setdefault("description", []).append(orig)
        return self.description


    def instruction(self, lc, orig, data):
        if lc.startswith("then "):
            data[-1]["steps"][-1]["expectedResult"] = [orig]
            return self.expectedresult
        data[-1]["steps"][-1]["instruction"].append(orig)
        return self.instruction


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


    def after_and(self, lc, orig, data):
        if lc.startswith("when "):
            data[-1]["steps"].append({"instruction": [orig]})
            return self.instruction
        data[-1]["steps"][-1]["expectedResult"].extend([self._orig_and, orig])
