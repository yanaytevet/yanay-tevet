import random
import string

from django.test import SimpleTestCase

from common.string_utils import StringUtils


class CreateRandomHashTest(SimpleTestCase):
    """`create_random_hash` is what a password-reset access id is drawn from, so these are secrecy
    tests rather than formatting ones."""

    def test_has_the_asked_for_length(self) -> None:
        self.assertEqual(len(StringUtils.create_random_hash(18)), 18)

    def test_uses_only_upper_case_letters_and_digits(self) -> None:
        alphabet = set(string.ascii_uppercase + string.digits)
        self.assertTrue(set(StringUtils.create_random_hash(200)).issubset(alphabet))

    def test_is_not_reproducible_from_a_seeded_random_module(self) -> None:
        """The regression guard.

        Drawing from `random` makes an access id a function of the Mersenne Twister's state, which
        a handful of earlier outputs is enough to recover — so anyone who has asked for a few reset
        links can compute the next one. Seeding the module and drawing twice is how that shows up:
        with `random` the two runs are identical, with a CSPRNG they are not.
        """
        random.seed(20260817)
        first = StringUtils.create_random_hash(32)
        random.seed(20260817)
        second = StringUtils.create_random_hash(32)
        self.assertNotEqual(first, second)

    def test_does_not_repeat_itself(self) -> None:
        hashes = {StringUtils.create_random_hash(18) for _ in range(200)}
        self.assertEqual(len(hashes), 200)
