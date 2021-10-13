# -*- coding: utf-8 -*-

# Copyright © 2021 Waldo Luis Ribeiro
# Released under the terms of the GNU General Public Licence, version 3
# <http://www.gnu.org/licenses/>

from __future__ import annotations

__license__ = 'GPL v3'
__author__ = 'Waldo Luis Ribeiro'

import csv
import os
import random
import re

import zhon.hanzi

from utils import index_of_first


class Hanzi:
    def __init__(self, hanzi: str, frequency: int = 1) -> None:
        self.hanzi = hanzi
        self.frequency = frequency
        self.occurrences = []  # list of indices where hanzi occurs
        self.distance = None
        self.example_sentences = []

    def calculate_average_distance(self) -> None:
        """
        Calculates the average distance between occurrences.

        :return: None
        :rtype: None
        """
        if self.frequency > 1:
            total_distance = 0
            for i in range(1, len(self.occurrences)):
                total_distance += self.occurrences[i] - self.occurrences[i - 1]
            self.distance = round(total_distance / (len(self.occurrences) - 1))
        elif self.frequency == 1:
            self.distance = 0

    def find_example_sentences(self, sentences: list[str]) -> None:
        """
        Finds example sentences in text.

        :param sentences: List of sentences in which to look for example sentences
        :type sentences: list

        :raises ValueError: No example sentences found

        :return: None
        :rtype: None
        """
        for sentence in sentences:
            if self.hanzi in sentence:
                self.example_sentences.append(sentence)
        if len(self.example_sentences) == 0:
            raise ValueError(f'could not find example sentences for "{self.hanzi}"')

    def get_random_example_sentences(self, how_many: int) -> list[str]:
        """
        Returns a list comprising a random sample of example sentences,
        or an empty list of no example sentences are available.

        :param how_many: Number of example sentences to return
        :type how_many: int

        :return: Returns a list of specified number (or fewer) example sentences
        :rtype: list
        """
        try:
            return random.sample(self.example_sentences, min(how_many, len(self.example_sentences)))
        except (ValueError, TypeError):
            return []


class Book:
    def __init__(self, title: str, text: str) -> None:
        """
        Initialises new book.

        :param title: Book title
        :type title: str
        :param text: Book text
        :type text: str

        :raises ValueError: No hanzi found in text provided

        :return: None
        :rtype: None
        """
        self.title = title
        self.text = text
        self.sentences = []
        self.hanzi = {}  # key: hanzi string, value: Hanzi object
        self.hanzi_sorted = ([], None, None)  # (sorted list of hanzi, reverse frequency, reverse distance)
        self.total_hanzi = 0
        self.statistics = []  # [(statistic heading, statistic value)]
        print(f'- created book entitled "{title}"')
        try:
            self.prepare_for_export()
        except ValueError:
            raise

    def prepare_for_export(self) -> None:
        """
        Prepares the book for export.

        :raises ValueError: No hanzi or valid sentences found

        :return: None
        :rtype: None
        """
        print(f'- preparing "{self.title}" for export')
        try:
            self.find_and_process_unique_hanzi()
        except ValueError:
            raise
        self.sort_hanzi()
        self.calculate_statistics()
        print(f'- prepared "{self.title}" for export')

    def find_and_process_unique_hanzi(self) -> None:
        """
        Finds and processes all the unique hanzi in the book. In particular, all unique hanzi are identified,
        their frequency is calculated and the indices of their occurrences are recorded, after which the book's
        text is split into sentences. The hanzi's average distance is then calculated and example sentences are
        identified.

        :raises ValueError: No hanzi or valid sentences found

        :return: None
        :rtype: None
        """
        print(f'- finding and processing all unique hanzi in "{self.title}"')

        # find all unique hanzi in book
        self.hanzi.clear()
        for index, character in enumerate(self.text):
            if re.fullmatch('[\u4e00-\u9fff]', character):  # \u4e00-\u9fff is unicode range for Chinese characters
                if character not in self.hanzi:
                    self.hanzi[character] = Hanzi(character)
                else:
                    self.hanzi[character].frequency += 1
                self.hanzi[character].occurrences.append(index)
        # if no hanzi found, book is not in Chinese
        if len(self.hanzi) == 0:
            raise ValueError(f'no hanzi found in "{self.title}"')

        # split book into sentences
        start_sentence = zhon.hanzi.characters + r'\w'
        latin_non_stops = r'\.\-#(),;:%$&*+/<=>@\[\]^_`{|}~\\ '
        mid_sentence = start_sentence + zhon.hanzi.radicals + zhon.hanzi.non_stops + r'─．○' + latin_non_stops
        latin_stops = r'!?'
        chinese_stops = zhon.hanzi.stops + r'…\n'
        stops = chinese_stops + latin_stops
        end_sentence = f'[{stops}][」﹂”』’》）］｝〕〗〙〛〉】]*'

        self.sentences = [sentence.strip() for sentence in re.findall(
            fr'([{start_sentence}]+[{mid_sentence}]*{end_sentence})',
            self.text
        )]

        if len(self.sentences) == 0:
            raise ValueError(f'no valid sentences found in {self.title}')

        for hanzi in self.hanzi.values():
            getattr(hanzi, 'calculate_average_distance')()
            try:
                getattr(hanzi, 'find_example_sentences')(self.sentences)
            except ValueError:
                raise

        print(f'- found and processed all unique hanzi in "{self.title}"')

    def sort_hanzi(self, frequency_reversed: bool = True, distance_reversed: bool = True) -> None:
        """
        Sorts self.hanzi. Assigns (sorted_list, frequency_order, distance_order) to self.hanzi_sorted.

        :param frequency_reversed: Reverse frequency, defaults to `True`
        :type frequency_reversed: bool
        :param distance_reversed: Reverse distance, defaults to `True`
        :type distance_reversed: bool

        :return: None
        :rtype: None
        """
        if self.hanzi_sorted[1] == frequency_reversed and self.hanzi_sorted[2] == distance_reversed:
            print(f'- hanzi already sorted '
                  f'(frequency_reversed: {frequency_reversed}; distance_reversed: {distance_reversed})')
        else:
            print(f'- sorting hanzi in {self.title} '
                  f'(frequency_reversed: {frequency_reversed}; distance_reversed: {distance_reversed})')
            hanzi_list = list(self.hanzi.values())
            for key, reverse in reversed((('frequency', frequency_reversed), ('distance', distance_reversed))):
                hanzi_list.sort(key=lambda hz: getattr(hz, key), reverse=reverse)
            self.hanzi_sorted = (hanzi_list, frequency_reversed, distance_reversed)
            print(f'- sorted hanzi in "{self.title}"')

    @staticmethod
    def export_csv(path: str, filename: str, hanzi_to_export: list[Hanzi], example_sentences: int) -> None:
        """
        Exports CSV.

        :param path: Export path
        :type path: str
        :param filename: CSV filename
        :type filename: str
        :param hanzi_to_export: List of hanzi to export
        :type hanzi_to_export: list
        :param example_sentences: Number of example sentences
        :type example_sentences: int

        :raises IOError: Path not writable

        :return: None
        :rtype: None
        """
        try:
            with open(os.path.join(path, filename), 'w', newline='', encoding='utf_8_sig') as f:
                csv_writer = csv.writer(f)
                headings = ['hanzi', 'freq', 'dist']
                for i in range(1, example_sentences + 1):
                    headings.append(f'ex{i}')
                csv_writer.writerow(headings)
                for hanzi in hanzi_to_export:
                    entry = [getattr(hanzi, 'hanzi'), getattr(hanzi, 'frequency'), getattr(hanzi, 'distance')]
                    examples = getattr(hanzi, 'get_random_example_sentences')(example_sentences)
                    entry.extend(examples)
                    csv_writer.writerow(entry)
        except IOError:
            print(f'- could not export "{filename}" to "{path}"')
            raise

    def export_unique_hanzi(self, path: str, frequency_reversed: bool = True, distance_reversed: bool = True,
                            example_sentences: int = 0) -> None:
        """
        Exports sorted unique hanzi as CSV.

        :param path: Export path
        :type path: str
        :param frequency_reversed: Reverse frequency, defaults to `True`
        :type frequency_reversed: bool
        :param distance_reversed: Reverse distance, defaults to `True`
        :type distance_reversed: bool
        :param example_sentences: Number of example sentences, defaults to 0
        :type example_sentences: int

        :raises IOError: Path not writable

        :return: None
        :rtype: None
        """
        # only sort self.hanzi if not already sorted in the specified order
        if self.hanzi_sorted[1] != frequency_reversed or self.hanzi_sorted[2] != distance_reversed:
            self.sort_hanzi(frequency_reversed, distance_reversed)
        print(f'- exporting unique hanzi in "{self.title}" '
              f'(frequency_reversed: {frequency_reversed}; distance_reversed: {distance_reversed})')
        try:
            Book.export_csv(path, f'{self.title}_hanzi.csv', self.hanzi_sorted[0], example_sentences)
        except IOError:
            raise
        print(f'- exported unique hanzi in "{self.title}" to "{path}"')

    def export_hanzi_to_learn(self, path: str, comprehension_percentage: int, frequency_threshold: int,
                              example_sentences: int, frequency_reversed: bool = True,
                              distance_reversed: bool = True) -> None:
        """
        Determines which hanzi to learn based on the desired comprehension
        percentage and frequency threshold, and exports them, along with
        example sentences, to a CSV.

        :param path: Export path
        :type path: str
        :param comprehension_percentage: Comprehension percentage
        :type comprehension_percentage: int
        :param frequency_threshold: Frequency threshold (if no exact match, match lower)
        :type frequency_threshold: int
        :param example_sentences: Number of example sentences
        :type example_sentences: int
        :param frequency_reversed: Reverse frequency, defaults to `True`
        :type frequency_reversed: bool
        :param distance_reversed: Reverse distance, defaults to `True`
        :type distance_reversed: bool

        :raises IOError: Path not writable

        :return: None
        :rtype: None
        """
        print(f'- exporting hanzi to learn in "{self.title}" (comprehension_percentage: {comprehension_percentage}; '
              f'frequency_threshold: {frequency_threshold}; example_sentences: {example_sentences}; '
              f'frequency_reversed: {frequency_reversed}; distance_reversed: {distance_reversed})')

        # sum frequency of hanzi up to last_hanzi_index as percentage of book text in percentage_of_total
        self.sort_hanzi(frequency_reversed, distance_reversed)
        last_hanzi_index = 0
        if comprehension_percentage != 100:
            percentage_of_total = 0.0
            while round(percentage_of_total, 2) < float(comprehension_percentage):
                percentage_of_total += getattr(self.hanzi_sorted[0][last_hanzi_index],
                                               'frequency') / self.total_hanzi * 100
                last_hanzi_index += 1
        else:
            last_hanzi_index = len(self.hanzi_sorted[0]) - 1

        # find first hanzi with specified threshold frequency (or lower, if no exact match)
        first_hanzi_index = index_of_first(self.hanzi_sorted[0],
                                           lambda x: getattr(x, 'frequency') <= frequency_threshold)

        # hanzi_to_learn comprises the hanzi with the specified frequency threshold
        # or below, until the specified comprehension percentage is attainable, but
        # if first_z_ind is -1 (returned by index_of_first if no match is found) or greater,
        # than last_hanzi_index, hanzi_to_learn will be empty because of how Python handles slicing
        hanzi_to_learn = self.hanzi_sorted[0][first_hanzi_index:last_hanzi_index + 1]

        print(f'- hanzi to learn: {len(hanzi_to_learn)}')
        try:
            Book.export_csv(path, f'{self.title}_learn.csv', hanzi_to_learn, example_sentences)
        except IOError:
            raise
        print(f'- exported hanzi to learn in "{self.title}" to "{path}"')

    @staticmethod
    def export_shared_hanzi(books: list[Book], path: str, frequency_reversed: bool = True) -> None:
        """
        Finds the hanzi shared by all the books in a list of books, sums their
        frequencies and exports a CSV with the shared hanzi and their summed frequencies.

        :param books: List of books to include in exported CSV
        :type books: list
        :param path: Export path
        :type path: str
        :param frequency_reversed: Reverse frequency, defaults to `True`
        :type frequency_reversed: bool

        :raises IOError: Path not writable

        :return: None
        :rtype: None
        """
        print('- exporting shared hanzi csv')
        # list of unique hanzi in each book
        book_hanzi = [book.hanzi.keys() for book in books]
        # find hanzi in common
        shared_hanzi = set.intersection(*map(set, book_hanzi))
        # sum up the frequency of each shared hanzi
        total_frequency = {hanzi: sum(getattr(book, 'hanzi')[hanzi].frequency for book in books)
                           for hanzi in shared_hanzi}
        # sort dictionary of shared hanzi
        total_frequency_sorted = sorted(total_frequency.items(), key=lambda hz: hz[1], reverse=frequency_reversed)
        try:
            with open(os.path.join(path, 'shared-hanzi.csv'), 'w', newline='', encoding='utf_8_sig') as f:
                f.write(f'hanzi,frequency\n')
                for hanzi, frequency in total_frequency_sorted:
                    f.write(f'{hanzi},{frequency}\n')
        except IOError:
            raise
        print(f'- exported shared hanzi csv to "{path}"')

    def calculate_statistics(self) -> None:
        """
        Calculates statistics. Assigns resulting list to self.statistics.

        :return: None
        :rtype: None
        """
        self.statistics.clear()

        print(f'- calculating statistics for "{self.title}"')

        percentiles = [1, 2, 5, 10, 15, 20, 30, 40, 50]

        # total number of hanzi
        self.total_hanzi = sum(getattr(hz, 'frequency') for hz in self.hanzi_sorted[0])
        self.statistics.append(('total hanzi', f'{self.total_hanzi:d}'))

        # total number of unique hanzi
        tally_unique_hanzi = len(self.hanzi_sorted[0])
        self.statistics.append((f'total unique hanzi', f'{tally_unique_hanzi:d}'))

        # most frequent hanzi as percentage of total number of hanzi
        most_frequent_hanzi_as_percentage_of_total = {}
        self.sort_hanzi()
        for i in percentiles:
            index_of_hanzi_at_percentile = round(i / 100 * len(self.hanzi_sorted[0]))
            most_frequent_hanzi_as_percentage_of_total[i] = sum(
                getattr(hanzi, 'frequency') for hanzi in
                self.hanzi_sorted[0][:index_of_hanzi_at_percentile]) / self.total_hanzi
            self.statistics.append(
                (f'top {i}% of hanzi as % of book', f'{most_frequent_hanzi_as_percentage_of_total[i]:%}'))
            self.statistics.append((f'no. hanzi in top {i}% of unique hanzi', f'{index_of_hanzi_at_percentile}'))

        print(f'- calculated statistics for "{self.title}"')

    def export_statistics(self, path: str) -> None:
        """
        Exports self.statistics as CSV.

        :param path: Export path
        :type path: str

        :raises IOError: Path not writable

        :return: None
        :rtype: None
        """
        print(f'- exporting statistics for "{self.title}"')
        try:
            with open(os.path.join(path, f'{self.title}_stats.csv'), 'w', newline='',
                      encoding='utf_8_sig') as stats_csv:
                headings, values = map(list, zip(*self.statistics))
                stats_csv.write(','.join(headings) + '\n')
                stats_csv.write(','.join(values) + '\n')
        except IOError:
            raise
        print(f'- exported statistics for "{self.title}" to "{path}"')

    @staticmethod
    def export_combined_statistics_csv(books: list[Book], path: str) -> None:
        """
        Exports statistics of all books in combined CSV.

        :param books: List of books to include in exported CSV
        :type books: list
        :param path: Export path
        :type path: str

        :raises IOError: Path not writable

        :return: None
        :rtype: None
        """
        print('- exporting combined statistics')
        csv_headings = []
        csv_values = []
        for index, book in enumerate(books):
            stat_headings, stat_values = map(list, zip(*book.statistics))
            stat_headings.insert(0, 'book title')
            stat_values.insert(0, book.title)
            if index == 0:
                csv_headings = stat_headings
            csv_values.append(stat_values)
        try:
            with open(os.path.join(path, 'combined-stats.csv'), 'w', newline='', encoding='utf_8_sig') as stats_csv:
                stats_csv.write(','.join(csv_headings) + '\n')
                for book_stats in csv_values:
                    stats_csv.write(','.join(book_stats) + '\n')
        except IOError:
            raise
        print(f'- exported combined statistics to {path}')
