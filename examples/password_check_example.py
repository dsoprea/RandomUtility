from password_check import LengthValidator, ComplexityValidator, \
                           DictionaryValidator, CommonSequenceValidator, \
                           PASSWORD_COMMON_SEQUENCES, ValidationError

def check_password(validator, password):
    description = ('%s("%s")' % (validator.__class__.__name__, password))

    try:
        validator(password)
    except ValidationError as e:
        result = str(e)
    else:
        result = 'OK'

    print("%s: %s" % (description, result))

length_validator = LengthValidator(8, 15)

complexity = { # A minimum of N upper-case letters.
               "UPPER": 2,
               
               # A minimum of N lower-case letters.
               "LOWER": 2,
               
               # A minimum of N digits.
               "DIGITS": 2,
              
               # A minimum of N punctuation characters.
               "PUNCTUATION": 2,

               # A minimum of N non-ASCII characters ("\xx")
               "NON ASCII": 0,

               # A minimum of N space-separated, unique words.
               "WORDS": 0 }

complexity_validator = ComplexityValidator(complexity)

dictionary_words = ['aaa', 'helloworld', 'mycompanyname', 'mybirthday']
dictionary_filepath = '/tmp/dictionary.txt'
with open(dictionary_filepath, 'w') as f:
    for word in dictionary_words:
        f.write(word)
        f.write("\n")

dictionary_validator = DictionaryValidator(dictionary='/tmp/dictionary.txt')
common_validator = CommonSequenceValidator(PASSWORD_COMMON_SEQUENCES)

print("")
check_password(length_validator, 'ab')
check_password(length_validator, 'abcdefghijklmnop')
check_password(length_validator, 'abcdefgh')

print("")
check_password(complexity_validator, 'simple')
check_password(complexity_validator, 'simpleAB')
check_password(complexity_validator, 'simpleAB01')
check_password(complexity_validator, 'simpleAB01;,')

print("")
check_password(dictionary_validator, 'mycompanyname')
check_password(dictionary_validator, 'mybirthday')
check_password(dictionary_validator, 'completelyrandompassword')

print("")
check_password(common_validator, '12345')
check_password(common_validator, 'qrstuv')
check_password(common_validator, 'nocommonsequences')

print("")

