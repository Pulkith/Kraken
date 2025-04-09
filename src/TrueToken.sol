// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 */
contract TRUEToken is ERC20, Ownable {
    address public administrator;
    
    event TokensMinted(address indexed to, uint256 amount);
    
    constructor(address _administrator) ERC20("TrueToken", "TRUE") Ownable(msg.sender) {
        administrator = _administrator;
        _mint(administrator, 1000000 * 10**decimals());
    }
    function mint(address to, uint256 amount) external {
        require(msg.sender == administrator || msg.sender == owner(), "Only administrator or owner can mint");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }
    function setAdministrator(address _newAdministrator) external onlyOwner {
        administrator = _newAdministrator;
    }
} 