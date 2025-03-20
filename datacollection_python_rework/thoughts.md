# setting up new python code structure

## Design goals

- Have *some* abscraction to avoid duplication.
- Avoid unnecessary imports, expecially of expensive imports like pythonsv & openipc
  - Read PPV codebase for their implimentation!
- Modularize everything so that individual functions can be mixed/matched freely at OTPL level.
- Wherever possible, write unit tests for functions.

## unit testing (chose `pytest`)

### idea
make formal unit tests (perhaps using unittest or pytest).
- This way, we can have a test suite for all the fuse overrides and ENSURE they work by running a new unit overnight with the test suite.
- Boot up, configure specific fuses, continue to EFI, verify.  If there are failures this will be reported, and if not we'll have confidence that everything works in isolation!
  - Plus, if a specific test does fail, the processor should be power-cycled regardless and hopefully the next test will work fine.
  - This test suite can be used when validating a new IFWI, as well.

### implementation
2023-09-12
- Currently writing tests for every Python function (very modular).  However, tests that involve fuse overrides take a looooong time, and they are split up individually.  (each one 5-10 min.)
- Could potentially write Python scripts that act as fuse recipes composed out of the functions already written (similar to current method in mtl codebase).  Would need separate set/verify recipes, but then it'd just be one test instead of multiple.  However, if something goes wrong, hard to say which fuse's fault.

2023-09-15
- Just wrote OTPL-level GCD fuse overrides recipe.  It took me ~3 hours total and is verbose and hard to read.  Next, I'll try an equivalent Python implementation...zs

## Questions

1. how many layers of abstraction?
   - I think at least 2: generic-product vs product-specific.
   - However, I think it's also possible to have product-generic vs derivative&stepping-specific inheritance.

2. How to group code?
    - *CMV's main job is to isolate specific blocks and test them at specific voltages/temperatures/frequencies*
    - Options
      1. Group by dielet first, then function
      2. Group by function first, then dielet
      3. Group just by function
      4. Group just by dielet


    - Idea for grouping voltage-set/read code
      - product-level
        - voltage_set_{method}.py script(s)
          - voltage_set_vfotf.py
          - voltage_set_dlvr.py
          - voltage_set_svid.py
        - voltage_read_nevo.py

    - Currently:
      - product-level
        - dielet
          - {dielet}_voltage.py  # contains set/read for everything related to dielet

    - also possible: all voltage stuff in one script (like with Fusion: voltage_control.py)

3. What to do with DOE code?  ex: [GCD AFS code](https://github.com/intel-innersource/applications.validation.circuit-margin.meteorlake.p.cdie-gcd-socnorth/blob/val/python/fuseovs_gcd.py).

  - Could make an experiments folder under MTL -> per-DOE folders?
  - Could make `afs.py` within gcd folder
  - Could put the code directly into `mtl.gcd.fuse_overrides.py`

## Specific, miscellaneous ideas

- define generic algorithms:
  - separate "poll with sleep until something happens with timeout" into an algorithm!  POST code reading and thermal soak both do this.

- investigate: is NEVO readback faster if we pass multiple voltage rail names in one call, or is it just as fast to read individual rails with multiple calls?

- profiling: try separating reading/printing into two different threads and/or processes.  time it!

- lot start: pysv start
- unit start: ensure unit is turned on, and can unlock, and is POSTed to 10AD.
- start on boot stage transition code + OTPL module.  The OTLP module needs to keep track of its state.  I'd also like the Python module to keep track of its state so I can add python checks when setting fuses.

## code structure to get around relative imports issue
- [https://stackoverflow.com/a/69099298](https://stackoverflow.com/a/69099298)
- [https://stackoverflow.com/a/50193944](https://stackoverflow.com/a/50193944)
- solution: add top-level folder to sys path in each script and perform all local imports relative to top-level.

## Done:
- Make the python log traceable!
  - Using Michael's PPV logger with minor changes.

- create object to keep track of NEVO
  - Idea
    - seems like there are setup/teardown steps involved
      - setup: nevo itself
      - setup/teardown: every time we want to read specific channel(s)
        - encapsulate this into a context manager!!

- define generic algorithms:
  - separate Hsin's DLVR set/readback loop - that can be a generic algorithm to which functions for set/read are passed.

- created object (PySvScriptManger) that wraps PythonSV scripts that import dielet variables / sv as globals.  Script is imported on first use and reloaded on subsequent uses.

    - Original concern: *Consult with someone on pythonsv team -- if different files having their own copies of dielet variables is an issue, then importing pythonsv scripts (ex: vf on the fly script) is an issue!  what should be done about this?*

- ProcessorInfo object
    - keeps track of p/d/s, qdf, visualid in a single object
    - physical : logical element mapping
  - Not implemented from original idea:
    - *per-dielet/domain information: is the domain enabled? if so, is the frequency floating, or locked and if so to what value?*

- bootstagetransitions: implemented as a module w a global variable to track current state
  - (idea) BootStageTransitioner object that:
    - keeps track of current state
    - provides functions that transition between states
    - provides functions to check current state
    - provide user-defined collection of states
    - ensures that unit is unlocked/refreshed only 1x / powerup?

- mtl.sv has get_{dielet} functions that take arguments to ensure that we're at a particular boot stage
  - (idea)fuse override functions: could make `ensure_at_*_fusebreak` functions into decorators?  Not sure if this would be clearer or the same or more confusing.

## Keep in mind
- Whenever I rename the repo, need to re-do all of the `sys.path.append()` blocks that put the script top-level repo on the system path

## Tab Save
- https://docs.intel.com/documents/PythonSv/PythonSv/overview/index.html
- https://docs.intel.com/documents/PythonSv/PythonSv/Training/pythonsv_bkms.html

- https://intelpypi.intel.com/pythonsv/production/namednodes/latest/+d/index.html
- https://intelpypi.intel.com/pythonsv/production/namednodes/latest/+doc/user_guide/index.html#nn-user-guide

- https://vtgvm-0272.amr.corp.intel.com/toolsdocs/ipccli/doc_ipccli_white/
- https://wiki.ith.intel.com/display/ITPII/OpenIPC
- https://wiki.ith.intel.com/display/ITPII

## singleton objects

I like the idea of having several singleton objects.  However, it turns out that the implementation of a singleton I'm using is tied to module importing.

If two modules import singleton.py (script containing singleton class) the same way, then the instance will be shared between them.
(ex: they live the same folder as singleton.py, so they both write `import singleton`)

However, if they use *different* imports (ex: one imports relative to itself, the other relative to project-top-level after sys.path append) the two module objects are SEPARATE and they'll each have a "singleton".  [StackOverflow](https://stackoverflow.com/a/52930277)

I could potentially put all the scripts into one folder (like our current MTL repo) to avoid this issue but I like the folder hierarchy...
If that's the case I'll need to standardize how the script import is done so everyone gets the same module and same singleton.