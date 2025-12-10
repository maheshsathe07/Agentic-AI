Why LangGraph? => to create a workflow in python we need lot of while loops, nested if else blocks then code will be messy and unstructured. to solve this issue to make workflow structure we use LangGraph. Helps to build the workflow.

terms:

1. Nodes => these are functions.
2. Edges => connection between the nodes to define the workflow.
3. State => it is a piece of data.
State: 
{input: str
 output: str
} 
graph.run(state).
to every node state has been pass, every node returns a state to pass it to the next node, and so on, finally the last state is returned once the final execution is done


conditional edge => if you are at a node based on a certain condition where needs to go.


Note: Once application got restart, the previous state will get vanished means llm don't have any context of the previous state then. To solve this issue we need to implement Checkpointing.

Checkpointing: the state of a thread at a particular point in time is called a checkpoint. It is a snapshot of the graph state saved at each super-step.