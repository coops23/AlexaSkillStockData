# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import stock_reader

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

YES_OR_NO_PROMPT = False
TICKER_SUGGESTION = ""
OPTION_FOR_SUGGESTION = ""


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to stock data! You can ask for the open price, high price, low price, volume, or change. Simply say your choice followed by the stock ticker."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class StockInfoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StockInfoIntent")(handler_input)

    def handle(self, handler_input):
        global YES_OR_NO_PROMPT
        global TICKER_SUGGESTION
        global OPTION_FOR_SUGGESTION

        slots = handler_input.request_envelope.request.intent.slots
        company_name = self.company_name_parser(slots['alpha_numeric_one'].value, slots['alpha_numeric_two'].value,
                                           slots['alpha_numeric_three'].value, slots['alpha_numeric_four'].value,
                                           slots['alpha_numeric_five'].value, slots['alpha_numeric_six'].value,
                                           slots['alpha_numeric_seven'].value, slots['alpha_numeric_eight'].value)
        option = str(slots['quote_fields'].value)

        speak_output = ""
        if company_name is None:
            speak_output += "Sorry, I was unable to understand what ticker you asked for. Could you try again?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        company_name = stock_reader.match_data(company_name)
        [status, info] = stock_reader.get_stock_data_yf(company_name)

        if not status:
            ticker = ""
            for letter in list(company_name):
                ticker += letter + " "
            '''
            best_suggestion = stock_reader.best_match_data(company_name)
            if best_suggestion is not None:
                best_suggestion = best_suggestion[0][0]
                suggested_ticker = ""
                for letter in list(best_suggestion):
                    if "." in letter:
                        suggested_ticker += "dot "
                    else:
                        suggested_ticker += letter + " "
                speak_output += "Sorry, ticker " + ticker + " does not exist. Did you mean " + suggested_ticker + "? "  # Ensure that you use the ticker rather than the company name. If you are not sure of the ticker you can search by using the keyword find followed by the suggestion."
                YES_OR_NO_PROMPT = True
                TICKER_SUGGESTION = best_suggestion
                OPTION_FOR_SUGGESTION = option
            else:
            '''
            speak_output += "Sorry, ticker. " + ticker + " does not exist. Please try something else."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response
        else:
            ticker = ""
            for letter in list(company_name):
                if "." in letter:
                    ticker += "dot "
                else:
                    ticker += letter + " "

            if "change" in option:
                speak_output += "Change of " + ticker + " is: " + info.change_percent + ". Or " + info.change + " points. "
            elif "previous close" in option:
                speak_output += "Previous close of " + ticker + " is: " + info.previous_close + ". "
            elif "volume" in option:
                speak_output += "Volume of " + ticker + " is: " + info.volume + ". "
            elif "low" in option:
                speak_output += "Low Price of " + ticker + " is: " + info.low + ". "
            elif "high" in option:
                speak_output += "High Price of " + ticker + " is: " + info.high + ". "
            elif "open" in option:
                speak_output += "Open Price of " + ticker + " is: " + info.open_price + ". "
            elif "price" in option:
                speak_output += "Price of " + ticker + " is: " + info.price + ". "

        return handler_input.response_builder.speak(speak_output).response


    def company_name_parser(self, alpha_numeric_one, alpha_numeric_two, alpha_numeric_three, alpha_numeric_four,
                        alpha_numeric_five, alpha_numeric_six, alpha_numeric_seven, alpha_numeric_eight):
        alpha_numeric = [alpha_numeric_one, alpha_numeric_two, alpha_numeric_three, alpha_numeric_four, alpha_numeric_five,
                         alpha_numeric_six, alpha_numeric_seven, alpha_numeric_eight]

        company_name = ""
        length = 0
        for char in alpha_numeric:
            if char is not None:
                char = str(char)
                company_name += char
                length += 1
        if length == 0:
            return None
        else:
            return company_name

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        global YES_OR_NO_PROMPT

        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input) and YES_OR_NO_PROMPT

    def handle(self, handler_input):
        global YES_OR_NO_PROMPT
        global TICKER_SUGGESTION
        global OPTION_FOR_SUGGESTION

        speak_output = ""
        option = OPTION_FOR_SUGGESTION

        [status, info] = stock_reader.get_stock_data_yf(TICKER_SUGGESTION)
        ticker = ""
        for letter in list(TICKER_SUGGESTION):
            if "." in letter:
                ticker += "dot "
            else:
                ticker += letter + " "

        if "change" in option:
            speak_output += "Change of " + ticker + " is: " + info.change_percent + ". Or " + info.change + " points. "
        elif "previous close" in option:
            speak_output += "Previous close of " + ticker + " is: " + info.previous_close + ". "
        elif "volume" in option:
            speak_output += "Volume of " + ticker + " is: " + info.volume + ". "
        elif "low" in option:
            speak_output += "Low Price of " + ticker + " is: " + info.low + ". "
        elif "high" in option:
            speak_output += "High Price of " + ticker + " is: " + info.high + ". "
        elif "open" in option:
            speak_output += "Open Price of " + ticker + " is: " + info.open_price + ". "
        elif "price" in option:
            speak_output += "Price of " + ticker + " is: " + info.price + ". "

        YES_OR_NO_PROMPT = False
        TICKER_SUGGESTION = ""
        OPTION_FOR_SUGGESTION = ""

        return handler_input.response_builder.speak(speak_output).response


class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        global YES_OR_NO_PROMPT

        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input) and YES_OR_NO_PROMPT

    def handle(self, handler_input):
        global YES_OR_NO_PROMPT
        global TICKER_SUGGESTION
        global OPTION_FOR_SUGGESTION

        speak_output = "Ok. Please try again."

        YES_OR_NO_PROMPT = False
        TICKER_SUGGESTION = ""
        OPTION_FOR_SUGGESTION = ""

        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can ask for the open price, high price, low price, volume, or change. Simply say your choice followed by the stock ticker."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StockInfoIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()