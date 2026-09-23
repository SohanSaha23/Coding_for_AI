"""
Program : Multi-Agent Intelligence Hub (MAIH)
Purpose : Maintains a global state registry for several autonomous agents -
          a dictionary of dictionaries holding each agent's position and
          accumulated knowledge - finds the knowledge common to every agent
          using set intersection, and relocates an agent safely by rebuilding
          its immutable coordinate tuple rather than trying to edit it.
Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Coding for AI - Week 5, Problem Set 5.1

DATA STRUCTURES IN PLAY
-----------------------
dict   agent_registry   AgentID -> {"Location": tuple, "Knowledge": set}
tuple  "Location"       fixed (x, y) coordinate pair, immutable by design
set    "Knowledge"      unordered, duplicate-free bag of Information Bits
dict   movement_log     AgentID -> list of every location the agent moved to

SUBMISSION NOTE: WHAT THE TypeError TELLS US ABOUT TUPLES IN MEMORY
--------------------------------------------------------------------
The TypeError comes from the tuple type itself, not from the interpreter
refusing a particular value: tuples simply do not implement __setitem__, the
method that item assignment calls. That absence is the whole point. A list
allocates a resizable array of references and keeps that array writable, so
assigning to a slot rewrites it in place and every name bound to the same list
sees the change at once. A tuple's sequence of references is fixed when the
object is constructed and is never rewritten, which is what lets Python cache
a tuple's hash and hand the same object to many owners without defensive
copying. So a coordinate pair stored as a tuple cannot be altered behind the
back of any code holding it. The only way to move an agent is to build a new
tuple and rebind the dictionary entry to it, which is exactly what
relocate_agent does.
"""

# -------------------------------------------------------------------------
# 3.1  Nested State Registry
# -------------------------------------------------------------------------
agent_registry = {
    "Agent_Alpha": {
        "Location": (10, 20),
        "Knowledge": {"grid_map", "comm_protocol", "telemetry_sync"},
    },
    "Agent_Beta": {
        "Location": (15, 5),
        "Knowledge": {"grid_map", "comm_protocol", "power_grid"},
    },
    "Agent_Gamma": {
        "Location": (0, 0),
        "Knowledge": {"grid_map", "comm_protocol", "power_grid",
                      "telemetry_sync"},
    },
}


# -------------------------------------------------------------------------
# 3.2  Knowledge Sync Logic
# -------------------------------------------------------------------------
def find_common_intelligence(registry):
    """Return the set of Information Bits known to EVERY agent.

    set.intersection() accepts any number of sets when called with the
    unpacking operator *, so this works unchanged whether the registry
    holds three agents or thirty - unlike writing
    alpha_knowledge & beta_knowledge & gamma_knowledge by hand, which
    would need rewriting every time an agent is added or removed.
    """
    knowledge_sets = [
        agent_data["Knowledge"] for agent_data in registry.values()
    ]
    return set.intersection(*knowledge_sets)


# -------------------------------------------------------------------------
# 3.3  Conflict Resolution and the Immutability Test
# -------------------------------------------------------------------------
def relocate_agent(registry, log, agent_id, new_location):
    """Move an agent, demonstrating first why the tuple cannot be edited."""
    # 1. Immutability demonstration - this attempt is MEANT to fail.
    print(f"Attempting direct mutation of {agent_id}'s Location tuple...")
    try:
        registry[agent_id]["Location"][0] = new_location[0]
    except TypeError as error:
        print(f"TypeError caught: {error}")
        print("Tuples are immutable; reassigning a new tuple instead.")

    # 2. Correct relocation - replace the whole entry with a new tuple.
    registry[agent_id]["Location"] = new_location

    # 3. Movement logging - creates the list on a first move, appends after.
    log.setdefault(agent_id, []).append(new_location)


# =========================================================================
# MAIN SCRIPT
# =========================================================================
print("--- Common Intelligence Across All Agents ---")
print(find_common_intelligence(agent_registry))

movement_log = {}

print("\n--- Relocating Agent_Alpha ---")
relocate_agent(agent_registry, movement_log, "Agent_Alpha", (12, 22))
print(f"\nAgent_Alpha new state: {agent_registry['Agent_Alpha']}")
print(f"Movement Log: {movement_log}")

print("\n--- Relocating Agent_Alpha again ---")
relocate_agent(agent_registry, movement_log, "Agent_Alpha", (14, 25))
print(f"Movement Log: {movement_log}")

# -------------------------------------------------------------------------
# 3.4  Efficiency Constraint: Summary Report (dictionary comprehension)
# -------------------------------------------------------------------------
summary_report = {
    agent_id: len(data["Knowledge"])
    for agent_id, data in agent_registry.items()
}

print("\n--- Summary Report (Dictionary Comprehension) ---")
print(summary_report)
