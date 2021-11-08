from flask import render_template,Blueprint
from validations import validating_inputs
from mongo_db import mongo

addition_api=Blueprint('addition_api',__name__)

@addition_api.route("/addition/<number1>/<number2>",methods=['POST','GET'])
def addition(number1,number2):
    # API to add numbers

    validation_output = validating_inputs.validating_inputs_function(number1,number2, operation='+')
    # goes to validations file and return results

    if validation_output == "Please Enter Numerical Values...!!!":
        return render_template('calculator.html', number1=number1, number2=number2,
                               operation='+', result=validation_output, calculation_success=False)
    number1 = validation_output[0]
    number2 = validation_output[1]
    calc_result=number1+number2
    try:
        if int(calc_result) / calc_result == 1:
            calc_result = int(calc_result)
    except ZeroDivisionError:
        if calc_result in (0, 0.0):
            calc_result = 0
    status = True
    calculation_done = ({'number1': number1, 'number2': number2,
                         'operation': '+', 'result': calc_result,
                         'calculation_success': status})
    mongo.inserting_into_calculation_collection(calculation_done) # inserting results in database
    mongo.updating_responses_collection('+',True) # inserting success count into database
    return render_template('calculator.html',
                           number1=number1,
                           number2=number2,
                           operation='+',
                           result=calc_result,
                           calculation_success=status) # for displaying output