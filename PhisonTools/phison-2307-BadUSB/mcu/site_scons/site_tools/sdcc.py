"""

XXX

"""
import os
import os.path

import SCons.Defaults
import SCons.Tool
import SCons.Util

class ToolSdccWarning(SCons.Warnings.Warning):
    pass

class SdccInvalidArch(ToolSdccWarning):
    pass

class SdccNotFound(ToolSdccWarning):
    pass

class SdccBug(ToolSdccWarning):
    pass

SCons.Warnings.enableWarningClass(ToolSdccWarning)

def findIt(program, env):
    # First search in the SCons path and then the OS path:
    prg = env.WhereIs(program) or SCons.Util.WhereIs(program)
    if prg:
        dir = os.path.dirname(prg)
        env.PrependENVPath('PATH', dir)
    else:
    	raise SCons.Errors.StopError(
        	SdccNotFound,
        	"Could not find \"%s\" program for SDCC compiler" % (program))
    return prg


MisleadArchs = { '8051' : 'mcs51' }
# arch : (asm,...)
Archs = { 'mcs51' : 	('sdas8051',), 
	'z80' : 	('sdasz80',), 
	'gbz80' : 	('sdasz80',),
	'z180' : 	('sdasz80',),
	'r2k' : 	('sdasrab',),
	'r3ka' : 	('sdasrab',),
	'ds390' : 	('sdas390',),
	'ds400' : 	('sdas390',),
	'pic16' : 	('gpasm',),	# !!! not in SDCC installation !!! TODO: make a separate tool
	'pic14' : 	('gpasm',),	# !!! not in SDCC installation !!! TODO: make a separate tool
	'hc08' : 	('sdas6808',),
	's08' : 	('sdas6808',),
	'TININative' : 	('macro',)} # !!! not in SDCC installation !!! TODO: make a separate tool
	
def _GetArch(env):
	if not 'TARGET_ARCH' in env:
		arch = 'NotDefinedArch'
	else:
		arch = env['TARGET_ARCH']
	if arch in MisleadArchs:
		arch = MisleadArchs[arch]
	if not arch in Archs:
		raise SCons.Errors.StopError(
			SdccInvalidArch,
			"Please specify valid TARGET_ARCH for SDCC: "+" ".join(Archs))		
	return arch
	
def _GetCpu(env):
	if not 'CPU' in env:
		cpu = 'defcpu'
	else:
		cpu = env['CPU']
	return cpu				

def _RelStaticObjectEmitter(target, source, env):
    targetBase, targetExt = os.path.splitext(SCons.Util.to_String(target[0]))
    for tgt in target:
        tgt.attributes.shared = None
    # side effects
    # asm
    env.SideEffect(targetBase+'.asm',target[0])
    env.Clean(target[0],targetBase+'.asm')
    # lst    
    env.SideEffect(targetBase+'.lst',target[0])
    env.Clean(target[0],targetBase+'.lst')
    # sym
    env.SideEffect(targetBase+'.sym',target[0])
    env.Clean(target[0],targetBase+'.sym')
    return (target, source)

def _prog_emitter(target, source, env):
    targetBase, targetExt = os.path.splitext(SCons.Util.to_String(target[0]))
    # side effects
    env.SideEffect(targetBase+'.lk',target[0])
    env.Clean(target[0],targetBase+'.lk')

    env.SideEffect(targetBase+'.mem',target[0])
    env.Clean(target[0],targetBase+'.mem')

    env.SideEffect(targetBase+'.map',target[0])
    env.Clean(target[0],targetBase+'.map')

    for src in source:
    	srcBase, srcExt = os.path.splitext(SCons.Util.to_String(src))
    	env.SideEffect(srcBase+'.rst',target[0])
    	env.Clean(target[0],srcBase+'.rst')
    
    return (target, source)

# current 3.4.0 SDCC version has bug in s-record extension handling: 
# s37 extension in forced if any other is specified, but no s-rec file is generated if s37 was specified with -o XXX.s37
# so as a temporary workaround: 1. we complain if user had specified something other that .s37 and  2. pass no extension in -o
# we should switch to generic _prog_emitter when SDCC team will fix this

def _srec_emitter(target, source, env):
    targetBase, targetExt = os.path.splitext(SCons.Util.to_String(target[0]))
    if targetExt!=".s37":
	raise SCons.Errors.StopError(
		SdccBug,
		"SDCC bug forces s-record file extension to .s37, please use .s37 (or empty) extension in Srec builders")		
    return _prog_emitter(target, source, env)

_srec_builder = SCons.Builder.Builder(
        action = SCons.Action.Action('$LINK $LINKFLAGS --out-fmt-s19 -o ${TARGET.filebase} $SOURCES $_LIBDIRFLAGS $_LIBFLAGS','$LINKCOMSTR'),
        suffix = '.s37', 
        src_suffix = '$OBJSUFFIX',                  
        src_builder = 'Object',
        emitter = _srec_emitter)

_bin_builder = SCons.Builder.Builder(
        action = SCons.Action.Action('$MAKEBIN $BINFLAGS $SOURCES $TARGET','$MAKEBINCOMSTR'),
        suffix = '.bin', 
        src_suffix = '.hex',                  
        src_builder = 'Hex',
        single_source=True)

###################################################################################

CSuffixes = ['.c']
if not SCons.Util.case_sensitive_suffixes('.c', '.C'):
    CSuffixes.append('.C')

ASSuffixes = ['.s', '.asm']
if SCons.Util.case_sensitive_suffixes('.s', '.S'):
    ASSuffixes.append('.S')
    ASSuffixes.append('.ASM')

def generate(env):
    env['TARGET_ARCH'] = _GetArch(env)
    env['TARGET_CPU'] = _GetCpu(env)

    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    # assembler
    for suffix in ASSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.ASAction)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)

    env['AS'] = Archs[env['TARGET_ARCH']][0]
    findIt(env['AS'], env)
    env['ASFLAGS']   = SCons.Util.CLVar('')
    env['ASCOM']     = '$AS $ASFLAGS -o $TARGET $SOURCES'

    # compiler
    for suffix in CSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CAction)
        static_obj.add_emitter(suffix, _RelStaticObjectEmitter)

    findIt('sdcc', env)
    env['CC']        = 'sdcc'
    env['CFLAGS']    = SCons.Util.CLVar('')
    env['CCCOM']     = '$CC $CFLAGS $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS -m$TARGET_ARCH -p$TARGET_CPU -c -o$TARGET $SOURCES'
    env['CPPDEFPREFIX']  = '-D'
    env['CPPDEFSUFFIX']  = ''
    env['INCPREFIX']  = '-I'
    env['INCSUFFIX']  = ''
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = True
    env['OBJSUFFIX'] = '.rel'
    env['CFILESUFFIX'] = '.c'

    # linker
    prog = SCons.Tool.createProgBuilder(env)
    env['LINK'] = '$CC'
    env['LINKFLAGS'] = SCons.Util.CLVar('')
    env['LINKCOM'] = '$LINK $LINKFLAGS -o $TARGET $SOURCES $_LIBDIRFLAGS $_LIBFLAGS'
    env['LIBDIRPREFIX'] = '-L'
    env['LIBDIRSUFFIX'] = ''
    env['PROGSUFFIX'] = '.hex'
    env['PROGEMITTER'] = _prog_emitter
    env['BUILDERS']['Hex'] = prog
    env['BUILDERS']['Srec'] = _srec_builder

    # makebin
    findIt('makebin', env)
    env['MAKEBIN'] = 'makebin'
    env['BINFLAGS'] = SCons.Util.CLVar('-p')
    env['BUILDERS']['Bin'] = _bin_builder

################################################################################

def exists(env):
    return findIt('sdcc', env)

#__all__ = ["generate", "exists"]
