###############################################################################
# Copyright (C) 2013 Dustin Oprea                                             #
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher       #
#                                                                             #
# See https://github.com/dsoprea/RandomUtility for the full collection of     #
# tools.                                                                      #
###############################################################################

from sys import stdout

class PromptAbortException(Exception):
    pass

# Python3: "raw_input" was renamed to "input" in Python3.

try:
    raw_input
except NameError:
    raw_input = input

_trunc_length = 10

def text_prompts(prompts):
    """Ask for a series of text responses from user. We expect a dictionary
    where the keys are the identifiers used in the resultant dictionary, and  
    the values are tuples of (label_text, is_required, default_value).
    """

    responses = {}
    j = 0
    do_space = False
    for id_, spec in prompts.items():
        if len(spec) == 5:
            (label_text, is_required, default_value, with_nl, 
             can_truncate_default) = spec
        else:
            (label_text, is_required, default_value) = spec
            with_nl = False
            can_truncate_default = True

        if default_value is None:
            default_value = ''
            if is_required is False:
                default_phrase = ' [""]'
            else:
                default_phrase = ''
        else:
            if can_truncate_default is True and \
               len(default_value) > _trunc_length:
                default_value_trunc = default_value[0:_trunc_length] + '...'
            else:
                default_value_trunc = default_value

            default_phrase = (' [CTRL+D for "%s"]' %
                              (default_value_trunc.
                                replace('\\', '\\\\').
                                replace('"', '\\"')))
        
        if is_required is True and default_phrase == '':
            required_phrase = ' (req)'
        else:
            required_phrase = ''        

        if do_space is True:
            print('')
            do_space = False

        prompt = ("%s%s%s:" % (label_text, default_phrase, required_phrase))

        if with_nl is True:
            print(prompt)
            input_prompt = ''
        else:
            input_prompt = prompt + ' '

        i = 0
        while 1:
            try:
                answer = raw_input(input_prompt).strip()
            except EOFError:
                """The user aborted the prompt (CTRL+D under Linux)."""
                print('')

                is_abort = True
                answer = default_value
            else:
                is_abort = False

            if is_required and (is_abort is True and default_value == '' or 
                                is_abort is False and answer == ''):
                i += 1

                if i >= 3:
                    raise PromptAbortException((id_, label_text))

                continue
            elif is_required is False and is_abort is True:
                answer = default_value
            
            break

        responses[id_] = answer
        j += 1
        if with_nl is True:
            do_space = True

    return responses

