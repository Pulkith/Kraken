// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./TRUEToken.sol";

/**
 * @title TrueVerification
 * @dev Handles the verification process for news items
 */
contract TrueVerification is Ownable {
    TRUEToken public trueToken;
    
    // News item struct
    struct NewsItem {
        string ipfsHash;
        uint256 verificationStart;
        uint256 trueVotes;
        uint256 falseVotes;
        bool verified;
        bool finalized;
        mapping(address => bool) hasVoted;
        mapping(address => bool) voteValue; // true = real, false = fake
        uint256 totalStaked;
    }
    
    // Maps news ID to its data
    mapping(uint256 => NewsItem) public newsItems;
    uint256 public newsCount;
    
    // Required token stake to vote
    uint256 public requiredStake = 10 * 10**18; // 10 TRUE tokens
    
    // Thresholds 
    uint256 public verificationThreshold = 90; // 90% for true votes to be verified
    uint256 public communityFlagThreshold = 10; // 10% for community flags to mark as fake
    
    // Events
    event NewsSubmitted(uint256 indexed newsId, string ipfsHash);
    event VoteCast(uint256 indexed newsId, address voter, bool voteValue);
    event NewsVerified(uint256 indexed newsId, bool isReal);
    event NewsFlagged(uint256 indexed newsId, address flagger);
    event RewardsDistributed(uint256 indexed newsId, address[] winners, uint256 totalReward);
    
    constructor(address _trueTokenAddress) Ownable(msg.sender) {
        trueToken = TRUEToken(_trueTokenAddress);
    }
    
    /**
     * @dev Submit a new news item for verification
     * @param _ipfsHash IPFS hash of the news content
     */
    function submitNews(string memory _ipfsHash) external onlyOwner {
        uint256 newsId = newsCount;
        NewsItem storage newItem = newsItems[newsId];
        
        newItem.ipfsHash = _ipfsHash;
        newItem.verificationStart = block.timestamp;
        newItem.verified = false;
        newItem.finalized = false;
        
        newsCount++;
        
        emit NewsSubmitted(newsId, _ipfsHash);
    }
    
    /**
     * @dev Cast a vote on a news item
     * @param _newsId ID of the news item
     * @param _voteValue true if real news, false if fake
     */
    function voteOnNews(uint256 _newsId, bool _voteValue) external {
        require(_newsId < newsCount, "News item does not exist");
        NewsItem storage item = newsItems[_newsId];
        
        require(!item.finalized, "Verification is finalized");
        require(!item.hasVoted[msg.sender], "Already voted");
        
        // Transfer tokens from voter to contract as stake
        trueToken.transferFrom(msg.sender, address(this), requiredStake);
        
        // Record vote
        item.hasVoted[msg.sender] = true;
        item.voteValue[msg.sender] = _voteValue;
        
        if (_voteValue) {
            item.trueVotes++;
        } else {
            item.falseVotes++;
        }
        
        item.totalStaked += requiredStake;
        
        emit VoteCast(_newsId, msg.sender, _voteValue);
        
        // Check if we can finalize verification
        checkAndFinalizeVerification(_newsId);
    }
    
    /**
     * @dev Check if verification can be finalized
     * @param _newsId ID of the news item
     */
    function checkAndFinalizeVerification(uint256 _newsId) internal {
        NewsItem storage item = newsItems[_newsId];
        uint256 totalVotes = item.trueVotes + item.falseVotes;
        
        // Need at least 10 votes to finalize
        if (totalVotes < 10) {
            return;
        }
        
        uint256 truePercentage = (item.trueVotes * 100) / totalVotes;
        
        if (truePercentage >= verificationThreshold) {
            item.verified = true;
            item.finalized = true;
            emit NewsVerified(_newsId, true);
            
            // Distribute rewards to true voters
            distributeRewards(_newsId, true);
        } else if (item.falseVotes > totalVotes / 2) { // Simple majority for fake news
            item.verified = false;
            item.finalized = true;
            emit NewsVerified(_newsId, false);
            
            // Distribute rewards to false voters
            distributeRewards(_newsId, false);
        }
    }
    
    /**
     * @dev Flag a verified news item as fake
     * @param _newsId ID of the news item
     */
    function flagNewsAsFake(uint256 _newsId) external {
        require(_newsId < newsCount, "News item does not exist");
        NewsItem storage item = newsItems[_newsId];
        
        require(item.verified && item.finalized, "News is not verified yet");
        
        emit NewsFlagged(_newsId, msg.sender);
        
        // This would typically trigger a review process
        // In a real implementation, this would collect flags and potentially revoke verification
    }
    
    /**
     * @dev Distribute rewards to winning voters
     * @param _newsId ID of the news item
     * @param _winningVote The winning vote value
     */
    function distributeRewards(uint256 _newsId, bool _winningVote) internal {
        NewsItem storage item = newsItems[_newsId];
        
        // Count winning voters
        uint256 winnerCount = _winningVote ? item.trueVotes : item.falseVotes;
        address[] memory winners = new address[](winnerCount);
        
        uint256 winnerIndex = 0;
        
        // Collect winning voters
        for (uint256 i = 0; i < newsCount; i++) {
            address voter = address(uint160(i)); // This is just a placeholder for the real implementation
            if (item.hasVoted[voter] && item.voteValue[voter] == _winningVote) {
                winners[winnerIndex] = voter;
                winnerIndex++;
            }
        }
        
        // Calculate reward per winner
        uint256 rewardPerWinner = item.totalStaked / winnerCount;
        
        // Distribute rewards
        for (uint256 i = 0; i < winnerCount; i++) {
            trueToken.transfer(winners[i], rewardPerWinner);
        }
        
        emit RewardsDistributed(_newsId, winners, item.totalStaked);
    }
    
    /**
     * @dev Change the required stake amount
     * @param _newStake New stake amount
     */
    function setRequiredStake(uint256 _newStake) external onlyOwner {
        requiredStake = _newStake;
    }
    
    /**
     * @dev Change the verification threshold percentage
     * @param _newThreshold New threshold (0-100)
     */
    function setVerificationThreshold(uint256 _newThreshold) external onlyOwner {
        require(_newThreshold <= 100, "Threshold must be 0-100");
        verificationThreshold = _newThreshold;
    }
    
    /**
     * @dev Change the community flag threshold percentage
     * @param _newThreshold New threshold (0-100)
     */
    function setCommunityFlagThreshold(uint256 _newThreshold) external onlyOwner {
        require(_newThreshold <= 100, "Threshold must be 0-100");
        communityFlagThreshold = _newThreshold;
    }
} 