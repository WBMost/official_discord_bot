# contains global vars to be used through out code :)
import inspect

# ==== FUNCTIONS ====

# ---- DEBUG ----
# +++ Logger +++
# overly advanced logger. Gross/hard to read for people just wanting a simple bot
DEFAULT_LOG_LEVEL = 0
LOG_LEVEL_NONE = -1
LOG_LEVEL_ERROR = 0
LOG_LEVEL_INFO = 1

class logger:
    def __init__(self) -> None:
        pass       

    def set_logging_level(self,level):
        global DEFAULT_LOG_LEVEL
        level = level.upper()
        if level == 'INFO':
            DEFAULT_LOG_LEVEL = LOG_LEVEL_INFO
        elif level == 'NONE':
            DEFAULT_LOG_LEVEL = LOG_LEVEL_NONE
        else:
            DEFAULT_LOG_LEVEL = LOG_LEVEL_ERROR


    def info(self,message, flush=True):
        if DEFAULT_LOG_LEVEL >= LOG_LEVEL_INFO:
            print('INFO: {}{}'.format(self._get_caller(),message,flush=flush))
    
    def error(self,message, flush=True):
        if DEFAULT_LOG_LEVEL >= LOG_LEVEL_ERROR:
            print('ERROR: {}{}'.format(self._get_caller(),message,flush=flush))

    def _get_caller(self):
        try:
            stack = inspect.stack()
            function = []
            for x in list(range(len(stack)-1,0,-1)):
                try:
                    f = stack[x]
                    func = f[3]
                    module = f[1].split('.')[0].split('/')[-1]
                    if module == 'bootstrap' or func == '_get_caller' or func == 'info' or func == 'error':
                        continue
                    function.append(func + '()')
                finally:
                    del f
            caller = '{}: '.format('.'.join(function))
        except:
            caller = ''
        return caller

# +++ debug_settings +++
# shitty class used to assist in debugging
class debug_vars():
    def __init__(self,debug):
        self.verbose = False
        self.debug = debug

    def get_debug(self) -> bool:
        return self.debug

    def set_debug(self,val:bool) -> None:
        '''
        Change debug value.
        !!! will make output more verbose !!!

        PARAMETERS
        -----------
        val : bool
        sets debug to be new bool value
        '''
        self.debug = val

    def get_verbose(self) -> bool:
        return self.verbose

    def set_verbose(self,val:bool) -> None:
        '''
        Change debug to be even more verbose. Would not recommend

        PARAMETERS
        -----------
        val : bool
        sets verbose to be new bool value
        '''
        self.verbose = val


# ==== MESSAGE_CONFIGS ====
# ---- EMOJIS ----
CURRENCY_EMOJI = '<:Bittersweet_Gtoken_NF2U:1087125360254136341>'


# ==== IMPORTANT_USERS ====
USERS = {
    
}