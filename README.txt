Disparate tools by published by Dustin. They are Python3 compatible.


Tools
=====

get_as_python: Convert data to Python code.

  Example: 

    get_as_python({ 'data1': { 'data22': { 'data33': 44 }}, 
                    'data2': ['aa','bb','cc'], 
                    'data3': ('dd','ee','ff') })

  Output (notice that a dict does not carry order, as expected):

    data1 = {"data22":{"data33":44}}
    data3 = ["dd","ee","ff"]
    data2 = ["aa","bb","cc"]

