"""
Questions:


    1. Complete the MiniVenmo.create_user() method to allow our application to create new users.

    2. Complete the User.pay() method to allow users to pay each other. Consider the following: if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this

    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the User.retrieve_activity() and MiniVenmo.render_feed() methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the User.add_friend() method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

import re
import unittest
import uuid


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:
    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class User:
    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.feed = []
        self.friends = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException("Username not valid.")

    def retrieve_feed(self):
        return self.feed

    def add_friend(self, new_friend):
        if new_friend is self:
            raise PaymentException("User cannot add themselves as a friend.")

        if new_friend in self.friends:
            raise PaymentException("User is already a friend.")

        self.friends.append(new_friend)
        new_friend.friends.append(self)

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException("Only one credit card per user!")

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException("Invalid credit card number.")

    def pay(self, target, amount, note):
        amount = float(amount)
        if self.balance >= amount:
            payment = self.pay_with_balance(target, amount, note)
        else:
            payment = self.pay_with_card(target, amount, note)

        self.feed.append(payment)
        target.feed.append(payment)

        return payment

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException("User cannot pay themselves.")

        elif amount <= 0.0:
            raise PaymentException("Amount must be a non-negative number.")

        elif self.credit_card_number is None:
            raise PaymentException("Must have a credit card to make a payment.")

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException("User cannot pay themselves.")

        if amount <= 0.0:
            raise PaymentException("Amount must be a non-negative number.")

        if self.balance < amount:
            raise PaymentException("Insufficient funds in balance.")

        self.balance -= amount
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match("^[A-Za-z0-9_\\-]{4,15}$", username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        user = User(username)
        user.add_to_balance(balance)
        user.add_credit_card(credit_card_number)
        return user

    def render_feed(self, feed):
        for item in feed:
            if isinstance(item, Payment):
                print(f"{item.actor.username} paid {item.target.username} ${item.amount:.2f} for {item.note}")

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):
    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()

    def test_create_user_sets_username(self):
        venmo = MiniVenmo()
        user = venmo.create_user("Bobby", 5.00, "4111111111111111")
        self.assertEqual(user.username, "Bobby")

    def test_create_user_sets_balance(self):
        venmo = MiniVenmo()
        user = venmo.create_user("Bobby", 5.00, "4111111111111111")
        self.assertEqual(user.balance, 5.00)

    def test_create_user_sets_credit_card(self):
        venmo = MiniVenmo()
        user = venmo.create_user("Bobby", 5.00, "4111111111111111")
        self.assertEqual(user.credit_card_number, "4111111111111111")

    def test_create_user_invalid_username(self):
        venmo = MiniVenmo()
        with self.assertRaises(UsernameException):
            venmo.create_user("ab", 5.00, "4111111111111111")

    def test_create_user_invalid_credit_card(self):
        venmo = MiniVenmo()
        with self.assertRaises(CreditCardException):
            venmo.create_user("Bobby", 5.00, "1234567890123456")

    def test_create_user_zero_balance(self):
        venmo = MiniVenmo()
        user = venmo.create_user("Bobby", 0.00, "4111111111111111")
        self.assertEqual(user.balance, 0.00)

    def test_pay_uses_balance_when_sufficient(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        carol = venmo.create_user("Carol", 0.00, "4242424242424242")

        bobby.pay(carol, 5.00, "Coffee")

        self.assertEqual(bobby.balance, 5.00)
        self.assertEqual(carol.balance, 5.00)

    def test_pay_uses_card_when_insufficient_balance(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 2.00, "4111111111111111")
        carol = venmo.create_user("Carol", 0.00, "4242424242424242")

        bobby.pay(carol, 5.00, "Coffee")

        self.assertEqual(bobby.balance, 2.00)
        self.assertEqual(carol.balance, 5.00)

    def test_pay_self_raises(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")

        with self.assertRaises(PaymentException):
            bobby.pay(bobby, 5.00, "Self")

    def test_pay_negative_amount_raises(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        carol = venmo.create_user("Carol", 0.00, "4242424242424242")

        with self.assertRaises(PaymentException):
            bobby.pay(carol, -5.00, "Negative")

    def test_pay_zero_amount_raises(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        carol = venmo.create_user("Carol", 0.00, "4242424242424242")

        with self.assertRaises(PaymentException):
            bobby.pay(carol, 0, "Zero")

    def test_pay_without_card_and_insufficient_balance_raises(self):
        bobby = User("Bobby")
        carol = User("Carol")
        bobby.add_to_balance(1.00)

        with self.assertRaises(PaymentException):
            bobby.pay(carol, 5.00, "No card")

    def test_pay_returns_payment_object(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 10.00, "4111111111111111")
        carol = venmo.create_user("Carol", 0.00, "4242424242424242")

        payment = bobby.pay(carol, 5.00, "Coffee")

        self.assertIsInstance(payment, Payment)
        self.assertEqual(payment.amount, 5.00)
        self.assertEqual(payment.actor.username, "Bobby")
        self.assertEqual(payment.target.username, "Carol")
        self.assertEqual(payment.note, "Coffee")

    def test_retrieve_feed_after_payment(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        bobby.pay(carol, 5.00, "Coffee")

        feed = bobby.retrieve_feed()
        self.assertEqual(len(feed), 1)
        self.assertIsInstance(feed[0], Payment)
        self.assertEqual(feed[0].actor.username, "Bobby")
        self.assertEqual(feed[0].target.username, "Carol")
        self.assertEqual(feed[0].amount, 5.00)
        self.assertEqual(feed[0].note, "Coffee")

    def test_feed_visible_to_both_users(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        bobby.pay(carol, 5.00, "Coffee")

        self.assertEqual(len(bobby.retrieve_feed()), 1)
        self.assertEqual(len(carol.retrieve_feed()), 1)

    def test_feed_multiple_payments(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        bobby.pay(carol, 5.00, "Coffee")
        carol.pay(bobby, 15.00, "Lunch")

        feed = bobby.retrieve_feed()
        self.assertEqual(len(feed), 2)
        self.assertEqual(feed[0].note, "Coffee")
        self.assertEqual(feed[1].note, "Lunch")

    def test_render_feed_output(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        bobby.pay(carol, 5.00, "Coffee")
        carol.pay(bobby, 15.00, "Lunch")

        import io
        import sys
        captured = io.StringIO()
        sys.stdout = captured
        venmo.render_feed(bobby.retrieve_feed())
        sys.stdout = sys.__stdout__

        output = captured.getvalue().strip().split("\n")
        self.assertEqual(output[0], "Bobby paid Carol $5.00 for Coffee")
        self.assertEqual(output[1], "Carol paid Bobby $15.00 for Lunch")

    def test_feed_empty_initially(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        self.assertEqual(len(bobby.retrieve_feed()), 0)

    def test_add_friend(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        bobby.add_friend(carol)

        self.assertIn(carol, bobby.friends)
        self.assertIn(bobby, carol.friends)

    def test_add_friend_is_bidirectional(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        bobby.add_friend(carol)

        self.assertEqual(len(bobby.friends), 1)
        self.assertEqual(len(carol.friends), 1)

    def test_add_self_as_friend_raises(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")

        with self.assertRaises(PaymentException):
            bobby.add_friend(bobby)

    def test_add_duplicate_friend_raises(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        bobby.add_friend(carol)
        with self.assertRaises(PaymentException):
            bobby.add_friend(carol)


if __name__ == "__main__":
    unittest.main()
