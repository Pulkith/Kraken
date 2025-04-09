// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract NewsGenTracker {
    struct Generation {
        uint256 timestamp;
        bytes32 id;
    }

    struct Metadata {
        string sources;
    }

    // Mapping from user to list of generations
    mapping(address => Generation[]) private userGenerations;

    // Mapping from ID to metadata
    mapping(bytes32 => Metadata) private idMetadata;

    // Mapping from user to ID existence
    mapping(address => mapping(bytes32 => bool)) private userHasID;

    /// @notice Add a new generation ID for a user, along with its metadata
    /// @param id The unique ID of the news generation (e.g. keccak256 hash)
    /// @param sources Metadata string (e.g., JSON) associated with the ID
    function addID(bytes32 id, string calldata sources) external {
        require(!userHasID[msg.sender][id], "ID already exists for user");

        Generation memory gen = Generation({
            timestamp: block.timestamp,
            id: id
        });

        userGenerations[msg.sender].push(gen);
        idMetadata[id] = Metadata({sources: sources});
        userHasID[msg.sender][id] = true;
    }

    /// @notice Get the latest ID for the user
    /// @return latestID The last added ID for msg.sender
    function getLatestID() external view returns (bytes32 latestID) {
        uint256 len = userGenerations[msg.sender].length;
        require(len > 0, "No IDs for user");
        latestID = userGenerations[msg.sender][len - 1].id;
    }

    /// @notice Check if the user has a specific ID
    /// @param user Address of the user
    /// @param id ID to check
    /// @return True if the user has that ID
    function hasID(address user, bytes32 id) external view returns (bool) {
        return userHasID[user][id];
    }

    /// @notice Get the sources metadata associated with an ID
    /// @param id The ID to look up
    /// @return sources Metadata string (e.g. JSON) associated with the ID
    function getMetadata(bytes32 id) external view returns (string memory sources) {
        require(bytes(idMetadata[id].sources).length > 0, "Metadata not found");
        return idMetadata[id].sources;
    }

    /// @notice Get all generation IDs and timestamps for the caller
    /// @return ids Array of IDs
    /// @return timestamps Array of timestamps
    function getAllIDsForUser() external view returns (bytes32[] memory ids, uint256[] memory timestamps) {
        uint256 len = userGenerations[msg.sender].length;
        ids = new bytes32[](len);
        timestamps = new uint256[](len);
        for (uint256 i = 0; i < len; i++) {
            ids[i] = userGenerations[msg.sender][i].id;
            timestamps[i] = userGenerations[msg.sender][i].timestamp;
        }
    }
}