// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ArticleRegistry {
    struct ArticleFile {
        string fileUri; // pointer
        uint256 uploadTime;
    }

    ArticleFile public latestFile;

    event FileUploaded(string fileUri, uint256 uploadTime);

    /// @notice Store the pointer to the JSON file on chain
    /// @param fileUri The file pointer (for example, the 0G Storage blob root)
    function uploadFile(string calldata fileUri) external {
        latestFile = ArticleFile(fileUri, block.timestamp);
        emit FileUploaded(fileUri, block.timestamp);
    }
}