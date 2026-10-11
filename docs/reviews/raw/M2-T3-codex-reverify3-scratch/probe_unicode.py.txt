import sys,json
sys.path.insert(0,'tests')
from test_commands import _cmd,_sim
from tars.sim.commands import BurnCommand
from tars.sim.burn_events import command_event
for name,f in [('constructor',lambda:BurnCommand(**_cmd(issuer='\ud800'))),('python_mapping',lambda:_sim().submit(_cmd(issuer='\ud800'))),('json',lambda:BurnCommand.model_validate_json(json.dumps(_cmd(issuer='\ud800'))))]:
 try:
  x=f();print(name,ascii(x));
  if hasattr(x,'status'):print('serialization',command_event(x).model_dump_json())
  else:print('serialization',x.model_dump_json())
 except Exception as e:print(name,type(e).__name__,ascii(str(e)))
