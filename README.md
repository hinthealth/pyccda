#pyccda

A Python library for CCDA XML files.

##Development notice

This project is under development and is not full-featured yet. However, pyccda is capable of
parsing CCDA XML files and converting them to structured ProtoRPC messages or simplified CSV
documents, which can be used to pipeline the data into data analysis tools.

##Usage

Before using, run `pip install -r requirements.txt` to install dependencies.

    import pyccda
    ccda = pyccda.CcdaDocument(<File pointer to a CCDA XML file.>)
    ccda.to_message()  # Returns CCDA represented as a ProtoRPC message.
    ccda.to_csv()  # Returns CCDA represented as a CSV.
    
##Running tests

    # Verifies basic functionality against test data.
    python ccda_test.py
