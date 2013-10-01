Disparate tools. They are Python3 compatible.


Tools
=====

get_as_python: Convert data to Python code.

  Example: 

    from get_as_python import get_as_python
check_password(complexity_validator, 'simple')
    get_as_python({ 'data1': { 'data22': { 'data33': 44 }}, 
                    'data2': ['aa','bb','cc'], 
                    'data3': ('dd','ee','ff') })

  Output (notice that a dict does not carry order, as expected):

    data1 = {"data22":{"data33":44}}
    data3 = ["dd","ee","ff"]
    data2 = ["aa","bb","cc"]

setup_support: Scripts to help with executable script placement during an 
               install.

    from setup_support import install_user_tool_symlink, \
                              install_su_tool_symlink

    # Place symlink $PREFIX/bin/module that points to whereever the Python 
    # module package.subpackage.module refers to. $PREFIX defaults to 
    # /usr/local.
    install_user_tool_symlink('package1.subpackage1.module1')

    # Same as above, but places in $PREFIX/sbin.
    install_su_tool_symlink('package2.subpackage2.module2')

password_check: A password strength-checker adapted from django-passwords.

    *See example for more information.

    from password_check import ComplexityValidator, ValidationError
    complexity = { ..complexity parameters.. }
    complexity_validator = ComplexityValidator(complexity)
    
    # Throws ValidationError.
    complexity_validator('simplepassword')    

