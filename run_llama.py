import os
import re
import sys
import json

from llama_cpp import Llama

class suppress_stdout_stderr(object):
    def __enter__(self):
        self.outnull_file = open(os.devnull, 'w')
        self.errnull_file = open(os.devnull, 'w')

        self.old_stdout_fileno_undup    = sys.stdout.fileno()
        self.old_stderr_fileno_undup    = sys.stderr.fileno()

        self.old_stdout_fileno = os.dup ( sys.stdout.fileno() )
        self.old_stderr_fileno = os.dup ( sys.stderr.fileno() )

        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

        os.dup2 ( self.outnull_file.fileno(), self.old_stdout_fileno_undup )
        os.dup2 ( self.errnull_file.fileno(), self.old_stderr_fileno_undup )

        sys.stdout = self.outnull_file        
        sys.stderr = self.errnull_file
        return self

    def __exit__(self, *_):        
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

        os.dup2 ( self.old_stdout_fileno, self.old_stdout_fileno_undup )
        os.dup2 ( self.old_stderr_fileno, self.old_stderr_fileno_undup )

        os.close ( self.old_stdout_fileno )
        os.close ( self.old_stderr_fileno )

        self.outnull_file.close()
        self.errnull_file.close()

def ask_llama(usr_q):
    system_prompt = f"""
    <<SYS>>
    Context:
    the solver choice will not depend on the characteristics of the computer
    the solver choice will depend on the characteristics of the simulation
    old computers cannot run omp, mpi and distributed parallelism because they have very few cores.
    very old computers usually have only one core.
    clusters are the best running mpi and distributed simulations.
    A laptops and personal computers are better running omp simulations.

    list of available solver nodes. use the simulation info to select the solver, not the characteristics of the computer in which it will run:
    "Structural" for structures, beams, loads
    "Fluid" for flows, fluids, CFD

    list of available strategy nodes:
    - "Dynamic" for dynamic simulations
    - "Static" for static simulations

    list of parallelism options. use the characteristics of the computer in which the simulation will run to select this:
    - "Serial" For serial with no parallelism. Suitable for very old computers or computers with limited computational power, and single core machines.
    - "OpenMP" For OpenMP. Suitable for muticore machines, workstations and laptopts.  
    - "MPI" For mpi and distributed simulations. Suitable for HPC centers, big clusters, and computers with high-end specs.
    <</SYS>>
    """

    usr_prompt = f"""
    [INST]
    Q:{usr_q}. select exactly one solver node, one stragy node and one parallelism option. select nodes only from the list provided. explain in a couple of sentences the selection and print a json file with the names of the selections. A:
    [/INST]
    """

    usr_prompt = f"""
    [INST]
    Q:{usr_q}. 
    Answer using at most one line.
    1 - Asses the properties of the simulation.
    2 - Asses the properties of the computer used to run the simulation.
    3 - With the information from 1 Select a solver node and shortly explain why. Use the key "solver".
    4 - With the information from 1 Select a strategy node and shortly explain why. Use the key "strategy".
    5 - With the information from 2 Select a parallelism option and shortly explain why. Use the key "parallelism".
    6 - Print a json file with the options selected with the format key:value and do not add extra info.
    A:
    [/INST]
    """

    prompt = f""" 
    {system_prompt}
    {usr_prompt}
    """

    with suppress_stdout_stderr():
        # Load the model
        LLM = Llama(model_path="./llama-2-7b-chat.Q5_K_M.gguf", n_ctx=2560)

        # Generate a response
        res_llm = LLM(prompt, max_tokens=512, stop=["Q:"], echo=False)

    return res_llm

# question = f"I want to run a Cantilever simulation in a HPC computing cluster"
output_solver = ask_llama(sys.argv[1])

# print("Q:", question)
print("A:", output_solver['choices'][0]['text'], file=sys.stderr)

# print("R: -Refined-")

r = re.search(r"\{[\S\s]*\}", output_solver['choices'][0]['text'])

if r:
    print(json.dumps(json.loads(r.group(0)), indent=4))
else:
    print('{error:"No usefull result"}')

# print("""
# {
#     "solver": "Structural",
#     "strategy": "DynamicStrategy",
#     "parallelism": "MPI"
# }
# """)