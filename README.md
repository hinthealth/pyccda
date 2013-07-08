#pyccda

A Python library for CCDA XML files.

##Development notice

This project is *under development* and is not fully-featured yet. However, pyccda is capable of
parsing CCDA XML files and converting them to structured ProtoRPC messages or simplified CSV
documents, which can be used to pipeline the data into data analysis tools.

##Usage

Before using, run `pip install -r requirements.txt` to install dependencies.

    import pyccda
    ccda = pyccda.CcdaDocument(open('ccda_file.xml'))

    # Returns CCDA represented as a simple CSV, which can be
    # useful to load data into an external data analysis tool.
    ccda.to_csv()

    # Returns CCDA represented as a protocol buffer message, for easy
    # data access and transfer between systems.
    ccda_message = ccda_doc.to_message()

    # Easily access health information using the protocol buffer message.
    ccda_message.allergies
    ccda_message.demographics
    ccda_message.immunizations
    ccda_message.labs
    ccda_message.medications
    ccda_message.problems
    ccda_message.procedures
    ccda_message.vitals

##Running tests

    # Verifies basic functionality against test data.
    python ccda_test.py
