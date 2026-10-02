from varopt import CandidateDecision, DecisionSpace


class ManufacturingScheduleSpace:
    """Test-only ForgeOpt-shaped decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        value = candidate.value

        return (
            isinstance(value, dict)
            and isinstance(value.get("operations"), tuple)
            and all(isinstance(operation, str) for operation in value["operations"])
        )


class VoyageRouteSpace:
    """Test-only NavOpt-shaped decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        value = candidate.value

        return (
            isinstance(value, tuple)
            and len(value) >= 2
            and all(isinstance(location, str) for location in value)
        )


class NetworkTopologySpace:
    """Test-only NexaOpt-shaped decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        value = candidate.value

        return (
            isinstance(value, frozenset)
            and all(
                isinstance(edge, tuple)
                and len(edge) == 2
                and all(isinstance(node, str) for node in edge)
                for edge in value
            )
        )


def test_manufacturing_schedule_decision_space():
    space: DecisionSpace = ManufacturingScheduleSpace()

    candidate = CandidateDecision(
        value={"operations": ("op-1", "op-2", "op-3")}
    )

    assert space.is_representable(candidate)


def test_voyage_route_decision_space():
    space: DecisionSpace = VoyageRouteSpace()

    candidate = CandidateDecision(
        value=("port-a", "port-b", "port-c")
    )

    assert space.is_representable(candidate)


def test_network_topology_decision_space():
    space: DecisionSpace = NetworkTopologySpace()

    candidate = CandidateDecision(
        value=frozenset(
            {
                ("node-a", "node-b"),
                ("node-b", "node-c"),
            }
        )
    )

    assert space.is_representable(candidate)


def test_same_core_contract_accepts_different_decision_shapes():
    spaces: list[DecisionSpace] = [
        ManufacturingScheduleSpace(),
        VoyageRouteSpace(),
        NetworkTopologySpace(),
    ]

    candidates = [
        CandidateDecision(
            value={"operations": ("op-1", "op-2")}
        ),
        CandidateDecision(
            value=("port-a", "port-b")
        ),
        CandidateDecision(
            value=frozenset({("node-a", "node-b")})
        ),
    ]

    assert all(space.is_representable(candidate) for space, candidate in zip(spaces, candidates))


def test_manufacturing_space_rejects_wrong_shape():
    space = ManufacturingScheduleSpace()

    assert not space.is_representable(
        CandidateDecision(value=("op-1", "op-2"))
    )


def test_voyage_route_space_rejects_wrong_shape():
    space = VoyageRouteSpace()

    assert not space.is_representable(
        CandidateDecision(value={"route": ("port-a", "port-b")})
    )


def test_network_topology_space_rejects_wrong_shape():
    space = NetworkTopologySpace()

    assert not space.is_representable(
        CandidateDecision(value=("node-a", "node-b"))
    )
