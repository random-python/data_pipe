import os
import sys
import traceback


def level1():

    def level2():

        try:
            raise NotImplementedError("No error")

        except Exception as e:

            exc_type, exc_value, exc_trace = sys.exc_info()

            print("---")
            print(f"exc_type={exc_type}")
            print(f"exc_value={exc_value}")
            print(f"exc_trace={exc_trace}")

            print("---")
            fname = os.path.split(exc_trace.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_trace.tb_lineno)

            print("---")
            print(traceback.format_exc())
            
    level2()

level1()
