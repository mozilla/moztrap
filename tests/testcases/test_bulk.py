import textwrap

from unittest2 import TestCase



class ParseBulkTest(TestCase):
    @property
    def parser(self):
        from ccui.testcases.bulk import BulkParser
        return BulkParser


    def test_success(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                 Test that bulk parsing works
                As a testcase administrator
                Given that I've loaded the bulk-input screen
                When I type a sonnet in the textarea
                And I sing my sonnet aloud
                Then my sonnet should be parsed
                And when I click the submit button
                Then testcases should be created
                And
                When I am done
                Then I feel satisfied
                
                  tEst that a second testcase works
                 With any old description
                  whEn I do this thing
                Over here
                tHen I see that thing  
                Over there
                """)
                ),
            [
                {
                    "name": "Test that bulk parsing works",
                    "description": [
                        "As a testcase administrator",
                        "Given that I've loaded the bulk-input screen"
                        ],
                    "steps": [
                        {
                            "instruction": [
                                "When I type a sonnet in the textarea",
                                "And I sing my sonnet aloud"
                                ],
                            "expectedResult": [
                                "Then my sonnet should be parsed",
                                ],
                            },
                        {
                            "instruction": [
                                "And when I click the submit button"
                                ],
                            "expectedResult": [
                                "Then testcases should be created"
                                ],
                            },
                        {
                            "instruction": ["When I am done"],
                            "expectedResult": ["Then I feel satisfied"],
                            },
                        ]
                    },
                {
                    "name": "tEst that a second testcase works",
                    "description": [
                        "With any old description"
                        ],
                    "steps": [
                        {
                            "instruction": [
                                "whEn I do this thing",
                                "Over here",
                                ],
                            "expectedResult": [
                                "tHen I see that thing",
                                "Over there",
                                ],
                            },
                        ],
                    },
                ]
            )


    def test_beginning_junk(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                This is not the beginning of a test case.
                Nor is this.
                """)
                ),
            [
                {
                    "error": (
                        "Expected 'Test that ...', not "
                        "'This is not the beginning of a test case.'"
                        ),
                    },
                ]
            )


    def test_no_description(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                When followed by the wrong keyword
                May not work out at all
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "error": (
                        "Expected at least one line of description before "
                        "'When followed by the wrong keyword'"
                        ),
                    },
                ]
            )


    def test_and_in_expected_result(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                test That the word And
                Yes, that word
                When I place it in an expected result
                then it works
                And
                is included in the result
                """)
                ),
            [
                {
                    "name": "test That the word And",
                    "description": ["Yes, that word"],
                    "steps": [
                        {
                            "instruction": [
                                "When I place it in an expected result",
                                ],
                            "expectedResult": [
                                "then it works",
                                "And",
                                "is included in the result",
                                ],
                            },
                        ]
                    },
                ]
            )


    def test_early_end_begin(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                """)
                ),
            [
                {
                    "error": (
                        "Unexpected end of input, looking for 'Test That '"
                        ),
                    },
                ]
            )


    def test_early_end_pre_description(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "error": (
                        "Unexpected end of input, looking for 'When ' or 'And When '"
                        ),
                    },
                ]
            )


    def test_early_end_description(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                With some description
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "description": [
                        "With some description",
                        ],
                    "error": (
                        "Unexpected end of input, looking for 'When ' or 'And When '"
                        ),
                    },
                ]
            )


    def test_early_end_instruction(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                And a good description
                When insufficiently assisted
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "description": [
                        "And a good description",
                        ],
                    "steps": [
                        {
                            "instruction": [
                                "When insufficiently assisted"
                                ],
                            },
                        ],
                    "error": (
                        "Unexpected end of input, looking for 'Then '"
                        ),
                    },
                ]
            )


    def test_early_end_after_and(self):
        self.assertEqual(
            self.parser().parse(
                textwrap.dedent("""
                Test That a perfectly good name
                And a good description
                When insufficiently assisted
                Then may not
                And
                """)
                ),
            [
                {
                    "name": "Test That a perfectly good name",
                    "description": [
                        "And a good description",
                        ],
                    "steps": [
                        {
                            "instruction": [
                                "When insufficiently assisted"
                                ],
                            "expectedResult": [
                                "Then may not"
                                ],
                            },
                        ],
                    "error": (
                        "Unexpected end of input, looking for 'When '"
                        ),
                    },
                ]
            )
