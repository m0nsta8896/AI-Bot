# components/utils/code_manager.py
import sys
import discord
import asyncio
import traceback
import re

async def execute_action(message, bot):
    async with message.channel.typing():
        print("AI action failed: Placeholder function was called.")
        asyncio.sleep(1)
        pass

class Code:
    async def execute(self, code: str, message, bot) -> tuple[bool, str]:
        try:
            temp_module = types.ModuleType("ai_temp_module")
            temp_module.__dict__.update(globals())
            temp_module.message = message
            temp_module.bot = bot
            
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            captured_output_temp = io.StringIO()
            captured_errors_temp = io.StringIO()
            sys.stdout = captured_output_temp
            sys.stderr = captured_errors_temp
            
            exec(code, temp_module.__dict__)
        except SyntaxError as e:
            error_message = f"AI-generated code has a Syntax Error during temporary compilation: {e}\n{traceback.format_exc()}"
            print(error_message)
            return False, captured_output_temp.getvalue() + captured_errors_temp.getvalue() + error_message
        except Exception as e:
            error_message = f"An unexpected error occurred during temporary compilation: {e}\n{traceback.format_exc()}"
            print(error_message)
            return False, captured_output_temp.getvalue() + captured_errors_temp.getvalue() + error_message
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        if "execute_action" not in temp_module.__dict__ or not asyncio.iscoroutinefunction(temp_module.execute_action):
            error_message = "AI code did not define a valid 'execute_action' async function in temporary module."
            print(error_message)
            return False, captured_output_temp.getvalue() + captured_errors_temp.getvalue() + error_message
        
        try:
            original_module = sys.modules[__name__]
            ai_func = temp_module.execute_action
            
            new_func = types.FunctionType(
                ai_func.__code__,
                globals(),
                'execute_action',
                ai_func.__defaults__,
                ai_func.__closure__
            )
            new_func.__qualname__ = 'execute_action'
            new_func.__module__ = __name__
            new_func.__doc__ = ai_func.__doc__
            new_func.__dict__.update(ai_func.__dict__)
            
            setattr(original_module, 'execute_action', new_func)
            
            captured_output_final = io.StringIO()
            captured_errors_final = io.StringIO()
            sys.stdout = captured_output_final
            sys.stderr = captured_errors_final
            
            await original_module.execute_action(message, bot)
            
            return True, captured_output_final.getvalue() + captured_errors_final.getvalue()
        except Exception as e:
            error_message = f"Error during dynamic function replacement or execution: {e}\n{traceback.format_exc()}"
            print(error_message)
            return False, captured_output_temp.getvalue() + captured_errors_temp.getvalue() + error_message
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            print(f"AI code execution finished. Captured Output:\n{captured_output_final.getvalue() if 'captured_output_final' in locals() else captured_output_temp.getvalue()}\nCaptured Errors:\n{captured_errors_final.getvalue() if 'captured_errors_final' in locals() else captured_errors_temp.getvalue()}")
    
    def extract(self, text):
        extracted_blocks = {
            "python": [],
            "monologue": [],
        }
        pattern = r"```(python|Internal Monologue)\n(.*?)\n```"
        for match in re.finditer(pattern, text, re.DOTALL | re.MULTILINE):
            language = match.group(1).lower()
            content = match.group(2).strip()
            
            if language == "python":
                extracted_blocks["python"].append(content)
            elif language == "internal monologue":
                extracted_blocks["monologue"].append(content)
        
        return extracted_blocks
code = Code()