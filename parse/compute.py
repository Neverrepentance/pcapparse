#!/usr/bin/python3
# coding=utf-8

probability_no_duplicate = 1.0

for i in range(100000000):
    probability_no_duplicate *= (9223372036854775807.0 - i) / 9223372036854775807.0

probability_with_duplicate = 1 - probability_no_duplicate

print("case:", probability_with_duplicate)


