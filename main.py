#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2021 Waldo Luis Ribeiro
# Released under the terms of the GNU General Public Licence, version 3
# <http://www.gnu.org/licenses/>

__license__ = 'GPL v3'
__version__ = '0.1'
__author__ = 'Waldo Luis Ribeiro'

import io
import os
import sys

import PySimpleGUI as sg

from book import Book

processed_books = {}


def export_books(book_file_names: list[str],
                 book_folder_path: str,
                 export_folder_path: str,
                 hanzi_export: tuple[int, bool, bool, int],
                 file_export: int,
                 learn_export: tuple[int, int, int, bool, bool],
                 stats_export: tuple[int, tuple[bool, bool, bool]]) -> None:
    """
    :param book_file_names: Book filenames
    :type book_file_names:  list
    :param book_folder_path: Book folder path
    :type book_folder_path: str
    :param export_folder_path: Export folder path
    :type export_folder_path: str
    :param hanzi_export: Parameters (mode, frequency_reverse, distance_reverse, usage_examples) for exporting
        unique hanzi, where mode may be 0 (None), 1 (Individual) or 2 (Shared), frequency_reverse may be `True`
        (sorted most to least frequent) or `False`, distance_reverse may be `True` (sorted most to least spaced)
        or `False`, and usage_examples is the number of example sentences to be exported alongside each hanzi.
    :type hanzi_export: tuple
    :param file_export: Which file(s) to export (0: unique hanzi, 1: hanzi to learn, 2: both).
        Only relevant if hanzi_exp mode == 1.
    :type file_export: int
    :param learn_export: Parameters (comprehension_percentage, frequency_threshold, usage_examples, frequency_reverse,
        distance_reverse) for exporting hanzi to learn, where frequency_reverse may be `True` (sorted most to least
        frequent) or `False` and distance_reverse may be `True` (sorted most to least spaced) or `False`.
    :type learn_export: tuple
    :param stats_export: Parameters (stats_export_mode, (total_hanzi, unique_hanzi, hanzi_percentiles)) for exporting
        statistics, where stats_export_mode may be 0 (none), 1 (individual) or 2 (combined), and total_hanzi,
        unique_hanzi and hanzi_percentiles may be `True` or `False`.
    :type stats_export: tuple

    :return: None
    :rtype: None
    """
    books_to_export = []

    for book_title in book_file_names:
        if book_title not in processed_books:
            book_path = os.path.join(book_folder_path, book_title + '.txt')
            try:
                with open(book_path) as book_file:
                    new_book = Book(book_title, book_file.read())
                    processed_books[book_title] = new_book
                    books_to_export.append(new_book)
                    print(f'- "{book_title}" added to processing list')
            except IOError:
                print(f'- could not access "{book_path}"')
            except ValueError as e:
                print(e)
                print(f'- could not process "{book_title}"')
        else:
            books_to_export.append(processed_books[book_title])
            print(f'- "{book_title}" added to processing list')

    if books_to_export:
        print('- all selected books added to processing list')
        # exporting hanzi in each individual book
        if hanzi_export[0] == 1:
            for book in books_to_export:
                # exporting list of unique hanzi
                if file_export == 0:
                    try:
                        book.export_unique_hanzi(export_folder_path, hanzi_export[1], hanzi_export[2], hanzi_export[3])
                    except IOError:
                        print(f'- could not export unique hanzi in "{book.title}"')
                # exporting hanzi to learn
                elif file_export == 1:
                    try:
                        book.export_hanzi_to_learn(export_folder_path, *learn_export)
                    except IOError:
                        print(f'- could not export hanzi to learn in "{book.title}"')
                # exporting both
                else:
                    try:
                        book.export_unique_hanzi(export_folder_path, hanzi_export[1], hanzi_export[2], hanzi_export[3])
                        book.export_hanzi_to_learn(export_folder_path, *learn_export)
                    except IOError:
                        print(f'- could not export unique hanzi or hanzi to learn in "{book.title}"')
        # exporting hanzi shared by all selected books
        elif hanzi_export[0] == 2:
            try:
                Book.export_shared_hanzi(books_to_export, export_folder_path, hanzi_export[1])
            except IOError:
                print('- could not export shared hanzi')
        # exporting a single file with the statistics of all the selected books
        if stats_export[0] == 2:
            try:
                Book.export_combined_statistics_csv(books_to_export, export_folder_path, stats_export[1])
            except IOError:
                print('- could not export combined statistics')
        # exporting the statistics of each selected book individually
        elif stats_export[0] == 1:
            for book in books_to_export:
                try:
                    book.export_statistics(export_folder_path, stats_export[1])
                except IOError:
                    print(f'- could not export statistics for "{book.title}"')
    else:
        print('- no books to process')


def disable_export_button(book_list: list[str], export_path: str, hanzi_mode: tuple[bool, bool, bool],
                          stats_mode: tuple[bool, bool, bool], stats_options: tuple[bool, bool, bool]) -> bool:
    """
    Decides whether to disable the export button.

    :param book_list: List of books in the book list
    :type book_list: list
    :param export_path: Export path
    :type export_path: str
    :param hanzi_mode: Hanzi export mode
    :type hanzi_mode: tuple
    :param stats_mode: Statistics export mode
    :type stats_mode: tuple
    :param stats_options: Statistics export options
    :type stats_options: tuple

    :return: Returns `True` if export button should be disabled, and vice versa.
    :rtype: bool
    """
    if len(book_list) == 0:
        return True
    elif len(export_path) == 0:
        return True
    elif hanzi_mode[0] and stats_mode[0]:
        return True
    elif len(book_list) == 1 and (hanzi_mode[2] or stats_mode[2]):
        return True
    elif (stats_mode[1] or stats_mode[2]) and (True not in stats_options):
        return True
    return False


def setup_window() -> sg.Window:
    path_frame = [
        [
            sg.Text("Books:"),
            sg.Input(
                enable_events=True,
                readonly=True,
                key='-BOOK PATH-'
            ),
            sg.FolderBrowse(target='-BOOK PATH-')
        ],
        [
            sg.Text("Export:"),
            sg.Input(
                enable_events=True,
                readonly=True,
                key='-EXPORT PATH-'
            ),
            sg.FolderBrowse(target='-EXPORT PATH-')
        ]
    ]

    book_sel_col = [
        [
            sg.Frame('Folders', path_frame),
        ],
        [
            sg.Frame('Books',
                     [
                         [
                             sg.Listbox(
                                 values=[],
                                 enable_events=True,
                                 select_mode=sg.PySimpleGUI.SELECT_MODE_EXTENDED,
                                 size=(60, 20),
                                 key='-BOOK LIST-'
                             )
                         ],
                         [
                             sg.Button(
                                 'Export',
                                 enable_events=True,
                                 expand_x=True,
                                 disabled=True,
                                 key='-EXPORT BUTTON-'
                             )
                         ]
                     ]
                     )
        ]
    ]

    exp_hanzi_mode_frame = [
        [
            sg.Radio(
                'None',
                'EXP_HANZI_MODE',
                enable_events=True,
                key='-HANZI MODE NONE-'
            )
        ],
        [
            sg.Radio(
                'Individual',
                'EXP_HANZI_MODE',
                enable_events=True,
                key='-HANZI MODE IND-',
                default=True
            )
        ],
        [
            sg.Radio(
                'Shared',
                'EXP_HANZI_MODE',
                enable_events=True,
                key='-HANZI MODE SHA-'
            )
        ]
    ]

    hanzi_sort_frame = [
        [
            sg.Radio(
                'Low > High',
                'EXP_HANZI_SORT',
                key='-HANZI SORT FORW-'
            )
        ],
        [
            sg.Radio(
                'High > Low',
                'EXP_HANZI_SORT',
                key='-HANZI SORT REV-',
                default=True
            )
        ]
    ]

    dist_sort_frame = [
        [
            sg.Radio(
                'Low > High',
                'EXP_DIST_SORT',
                key='-DIST SORT FORW-'
            )
        ],
        [
            sg.Radio(
                'High > Low',
                'EXP_DIST_SORT',
                key='-DIST SORT REV-',
                default=True
            )
        ]
    ]

    exp_opt_frame = [
        [
            sg.Radio(
                'Unique Hanzi',
                'EXP_FILES',
                enable_events=True,
                key='-EXP FILES HANZI-'
            )
        ],
        [
            sg.Radio(
                'Hanzi to Learn',
                'EXP_FILES',
                enable_events=True,
                key='-EXP FILES LEARN-',
                default=True
            )
        ],
        [
            sg.Radio(
                'Both',
                'EXP_FILES',
                enable_events=True,
                key='-EXP FILES BOTH-'
            )
        ]
    ]

    learn_frame = [
        [
            sg.Text('Usage examples:', size=16),
            sg.Spin(values=[i for i in range(0, 11)], initial_value=2, size=4, key='-USG EX SPIN-')
        ],
        [
            sg.Text('Comprehension:', size=16),
            sg.Spin(values=[i for i in range(90, 101)], initial_value=98, size=4, key='-COMP PERC SPIN-')
        ],
        [
            sg.Text('Frequency threshold:', size=16),
            sg.Spin(values=[i for i in range(10, 51)], initial_value=20, size=4, key='-FREQ THRESH SPIN-')
        ]
    ]

    exp_stats_mode_frame = [
        [
            sg.Radio(
                'None',
                'EXP_STATS_MODE',
                enable_events=True,
                key='-STATS MODE NONE-',
                default=True
            )
        ],
        [
            sg.Radio(
                'Individual',
                'EXP_STATS_MODE',
                enable_events=True,
                key='-STATS MODE IND-'
            )
        ],
        [
            sg.Radio(
                'Combined',
                'EXP_STATS_MODE',
                enable_events=True,
                key='-STATS MODE COM-'
            )
        ]
    ]

    exp_stats_options_frame = [
        [
            sg.Checkbox(
                'Total number of hanzi',
                disabled=True,
                enable_events=True,
                key='-STATS OPT HANZI-'
            )
        ],
        [
            sg.Checkbox(
                'Total number of unique hanzi',
                disabled=True,
                enable_events=True,
                key='-STATS OPT UNIQUE HANZI-'
            )
        ],
        [
            sg.Checkbox(
                'Hanzi percentiles (%)',
                disabled=True,
                enable_events=True,
                key='-STATS OPT HANZI PERC-'
            )
        ]
    ]

    config_col = [
        [
            sg.Frame('Hanzi',
                     [
                         [
                             sg.Frame('Mode', exp_hanzi_mode_frame),
                             sg.Frame('Frequency', hanzi_sort_frame, expand_y=True),
                             sg.Frame('Distance', dist_sort_frame, expand_y=True)
                         ],
                         [
                             sg.Frame('Export', exp_opt_frame),
                             sg.Frame('Learning', learn_frame, expand_y=True)
                         ]
                     ]
                     )
        ],
        [
            sg.Frame('Statistics',
                     [
                         [
                             sg.Frame('Mode', exp_stats_mode_frame),
                             sg.Frame('Options', exp_stats_options_frame)
                         ]
                     ],
                     expand_x=True
                     )
        ]
    ]

    layout = [
        [
            sg.Column(book_sel_col),
            sg.Column(config_col)
        ]
    ]

    return sg.Window('Chinese Book Analyser', layout)


def main():
    window = setup_window()

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        # assign values to lists to neaten up subsequent event handling
        disable_exp_btn_criteria = [
            values['-BOOK LIST-'],
            values['-EXPORT PATH-'],
            (
                values['-HANZI MODE NONE-'],
                values['-HANZI MODE IND-'],
                values['-HANZI MODE SHA-']
            ),
            (
                values['-STATS MODE NONE-'],
                values['-STATS MODE IND-'],
                values['-STATS MODE COM-']
            ),
            (
                values['-STATS OPT HANZI-'],
                values['-STATS OPT UNIQUE HANZI-'],
                values['-STATS OPT HANZI PERC-']
            )
        ]
        hanzi_sort_opt = ['-HANZI SORT FORW-', '-HANZI SORT REV-']
        dist_sort_opt = ['-DIST SORT FORW-', '-DIST SORT REV-']
        learn_sliders = ['-USG EX SPIN-',
                         '-COMP PERC SPIN-', '-FREQ THRESH SPIN-']
        exp_opt = ['-EXP FILES HANZI-',
                   '-EXP FILES LEARN-', '-EXP FILES BOTH-']

        # import folder was selected
        if event == '-BOOK PATH-':
            folder = values['-BOOK PATH-']
            if folder:
                # get list of files in folder
                file_list = os.listdir(folder)
                # get list of .txt files in folder
                filenames = [
                    f.removesuffix('.txt') for f in file_list
                    if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith('.txt')
                ]
                # show list of .txt files in listbox with key -BOOK LIST-
                window['-BOOK LIST-'].update(filenames)

        # export folder was selected
        elif event == '-EXPORT PATH-':
            window['-EXPORT BUTTON-'].update(disabled=disable_export_button(*disable_exp_btn_criteria))

        # enable/disable frequency/distance sorting options depending on selected hanzi export mode
        elif event == '-BOOK LIST-':
            window['-EXPORT BUTTON-'].update(disabled=disable_export_button(*disable_exp_btn_criteria))

        # hanzi export mode was altered
        elif event.startswith('-HANZI MODE'):
            if event.endswith('NONE-'):
                for elem in [*hanzi_sort_opt, *dist_sort_opt, *learn_sliders, *exp_opt]:
                    window[elem].update(disabled=True)
            elif event.endswith('IND-'):
                for elem in [*hanzi_sort_opt, *dist_sort_opt, *learn_sliders, *exp_opt]:
                    window[elem].update(disabled=False)
            elif event.endswith('SHA-'):
                for elem in [*hanzi_sort_opt]:
                    window[elem].update(disabled=False)
                for elem in [*dist_sort_opt, *learn_sliders, *exp_opt]:
                    window[elem].update(disabled=True)
            window['-EXPORT BUTTON-'].update(disabled=disable_export_button(*disable_exp_btn_criteria))

        # statistics export mode was altered
        elif event.startswith('-STATS MODE'):
            statistics_options_checkboxes = ['-STATS OPT HANZI-', '-STATS OPT UNIQUE HANZI-', '-STATS OPT HANZI PERC-']
            if event.endswith('NONE-'):
                for checkbox in statistics_options_checkboxes:
                    window[checkbox].update(disabled=True)
            else:
                for checkbox in statistics_options_checkboxes:
                    window[checkbox].update(disabled=False)
            window['-EXPORT BUTTON-'].update(disabled=disable_export_button(*disable_exp_btn_criteria))

        # statistics export option was altered
        elif event.startswith('-STATS OPT'):
            window['-EXPORT BUTTON-'].update(disabled=disable_export_button(*disable_exp_btn_criteria))

        # export button was selected and listbox item is selected
        elif event == '-EXPORT BUTTON-':
            if len(values['-BOOK LIST-']) >= 1:
                try:
                    if not os.path.exists(values['-EXPORT PATH-']):
                        os.makedirs(values['-EXPORT PATH-'])
                except IOError:
                    print(f'could not create directory "{values["-EXPORT PATH-"]}"')
                    break

                hanzi_export_mode = 1
                if values['-HANZI MODE NONE-']:
                    hanzi_export_mode = 0
                elif values['-HANZI MODE SHA-']:
                    hanzi_export_mode = 2

                file_export_option = 1
                if values['-EXP FILES HANZI-']:
                    file_export_option = 0
                elif values['-EXP FILES BOTH-']:
                    file_export_option = 2

                hanzi_frequency_order = True
                if values['-HANZI SORT FORW-']:
                    hanzi_frequency_order = False

                hanzi_distance_order = True
                if values['-DIST SORT FORW-']:
                    hanzi_distance_order = False

                stats_export_mode = 2
                if values['-STATS MODE NONE-']:
                    stats_export_mode = 0
                elif values['-STATS MODE IND-']:
                    stats_export_mode = 1

                stats_export_options = (
                    values['-STATS OPT HANZI-'],
                    values['-STATS OPT UNIQUE HANZI-'],
                    values['-STATS OPT HANZI PERC-']
                )

                comprehension_percentage = int(values['-COMP PERC SPIN-'])
                frequency_threshold = int(values['-FREQ THRESH SPIN-'])
                example_sentences = int(values['-USG EX SPIN-'])

                old_stdout = sys.stdout
                new_stdout = io.StringIO()
                sys.stdout = new_stdout

                export_books(
                    values['-BOOK LIST-'],
                    values['-BOOK PATH-'],
                    values['-EXPORT PATH-'],
                    (hanzi_export_mode, hanzi_frequency_order, hanzi_distance_order, example_sentences),
                    file_export_option,
                    (comprehension_percentage, frequency_threshold, example_sentences,
                     hanzi_frequency_order, hanzi_distance_order),
                    (stats_export_mode, stats_export_options)
                )

                sg.popup_scrolled(new_stdout.getvalue(), title='Export Log', size=(50, 20))
                sys.stdout = old_stdout

    window.close()


if __name__ == "__main__":
    main()
