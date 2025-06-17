# main.py
# import src.gdbi as gdb
import src.ragprocess as pp
import src.raginfer as ri
import argparse

from src.includes import SearchType
from src.ragagent import GraphRAGAgent


def preprocess(reload=None):
    """Preprocess and prepare the Graph Mapping KG environment"""
    gdbprocessor = pp.GraphRAGProcessor()
    # ! Only if starting from scratch for demo setup
    if reload is not None:
        print("Reloading chunks and preparing vector store...")
        gdbprocessor.prep(init=True)
    else:
        print("Updating vectors and embeddings...")
        gdbprocessor.prep(init=False)


def parse_args():
    """CLI Argument parser for the Graph Mapping KG demo"""
    parser = argparse.ArgumentParser(description="CSF Mapping KG demos")
    parser.add_argument("--debug", action="store_true", help="Debug/test for CSF Mapping KG env")
    subparser = parser.add_subparsers(dest="command")

    infer = subparser.add_parser("demo", help="Agentic inference demonstrations for CSF Mapping KG")
    prep = subparser.add_parser("prep", help="Chunk preprocessing + Vector store and embedding preparation utilities")

    infergroup = infer.add_mutually_exclusive_group(required=True)
    infergroup.add_argument(
        "--chat",
        help="Direct LLM inference with no augmentation",
        nargs="?",
        const="",
        type=str,
    )
    infergroup.add_argument(
        "--plain",
        help="Baseline LLM inference leveraging retrieval with vectors and embeddings (semantic search)",
        nargs="?",
        const="",
        type=str,
    )
    infergroup.add_argument(
        "--rag",
        help=(
            "Augmented LLM inference leveraging compiled content from existing mappings (semantic + episodic search)"),
        nargs="?",
        const="",
        type=str,
    )
    infergroup.add_argument(
        "--triage", help="Triaged generated LLM mappings from RAG inference", nargs="?", const="", type=str
    )

    nondemo = prep.add_mutually_exclusive_group(required=False)
    nondemo.add_argument("--reload", help="Re-process, load chunks", nargs="?", const="{}", type=str)
    args = parser.parse_args()
    return args


def infer_session(demoinfer, question=None, search_type=SearchType.CHAT):
    """Run a demo inference session with a question"""
    response = None
    if search_type == SearchType.CHAT:
        response = demoinfer.infer_chat(question)
    elif search_type == SearchType.PLAIN:
        response = demoinfer.infer_plain(question)
    elif search_type == SearchType.RAG:
        response = demoinfer.infer_rag(question)
    if response:
        print(search_type.name + " Inference response:", response)


def triage_session(input=None):
    """Run a triage session for generated mappings"""
    demoagent = GraphRAGAgent()
    response = demoagent.invoke(msg=input)
    if response:
        print("Triage Inference response:", response)
    else:
        print("Error in triage session.")


def run_session(args):
    demoinfer = ri.GraphInference()
    """Run demo session based on CLI arguments"""
    if args.command is None or args.debug is None or args.debug:
        print("Debugging CSF Mapping KG environment...")
        demoinfer.debug()
    elif args.command == "demo" and args.plain is not None:
        print("Running plain inference demo...")
        infer_session(demoinfer, question=args.plain, search_type=SearchType.PLAIN)
    elif args.command == "demo" and args.rag is not None:
        infer_session(demoinfer, question=args.rag, search_type=SearchType.RAG)
    elif args.command == "demo" and args.chat is not None:
        infer_session(demoinfer, question=args.chat, search_type=SearchType.CHAT)
    elif args.command == "demo" and args.triage is not None:
        triage_session(input=args.triage)
    elif args.command == "prep":
        preprocess(args.prep)
    else:
        print("Undefined utility test command. Options: demo, prep [debug]")


if __name__ == "__main__":
    builder_args = parse_args()
    run_session(builder_args)
    print("Demo session finished.")
