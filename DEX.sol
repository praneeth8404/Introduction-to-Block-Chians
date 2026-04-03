// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract LiquidityPool is ERC20 {
    IERC20 public tokenA;
    IERC20 public tokenB;

    uint256 public reserveA;
    uint256 public reserveB;

    constructor(address _tokenA,address _tokenB) ERC20("LP Token", "LPT") {
        require(_tokenA!=address(0),"Invalid tokenA address");
        require(_tokenB!=address(0),"Invalid tokenB address");
        require(_tokenA!=_tokenB,"Tokens must be different");
        tokenA=IERC20(_tokenA);
        tokenB=IERC20(_tokenB);
    }

    function deposit(uint256 amountA, uint256 amountB) external {
        require(amountA>0&&amountB>0,"Amounts must be greater than zero");
        uint256 liquidity;
        if(totalSupply()==0) {
            liquidity=sqrt(amountA*amountB);
        }else{
            require(reserveA*amountB==reserveB*amountA,"Deposit must match pool ratio");
            liquidity=(amountA*totalSupply())/reserveA;
        }
        reserveA+=amountA;
        reserveB+=amountB;

        tokenA.transferFrom(msg.sender,address(this),amountA);
        tokenB.transferFrom(msg.sender,address(this),amountB);
        _mint(msg.sender,liquidity);
    }

    function withdraw(uint256 lpAmount) external {
        require(lpAmount>0,"LP amount must be greater than zero");
        require(balanceOf(msg.sender)>=lpAmount,"Insufficient LP balance");
        uint256 amountA = (lpAmount*reserveA)/totalSupply();
        uint256 amountB = (lpAmount*reserveB)/totalSupply();

        require(amountA>0&&amountB>0,"Withdraw amount too small");
        _burn(msg.sender,lpAmount);

        reserveA-=amountA;
        reserveB-=amountB;

        tokenA.transfer(msg.sender,amountA);
        tokenB.transfer(msg.sender,amountB);
    }

    function swap(address tokenIn, uint256 amountIn, uint256 minOut) external {
        require(amountIn>0,"Amount must be greater than zero");
        require(tokenIn==address(tokenA)||tokenIn==address(tokenB),"Invalid input token");
        bool isTokenAIn = tokenIn == address(tokenA);

        uint256 inputReserve=isTokenAIn?reserveA:reserveB;
        uint256 outputReserve=isTokenAIn?reserveB:reserveA;

        uint256 amountInWithFee=amountIn*997;

        uint256 amountOut=(outputReserve*amountInWithFee)/(inputReserve*1000+amountInWithFee);
        require(amountOut>=minOut,"Slippage limit exceeded");
        require(amountOut>0,"Zero output amount");
        require(amountOut<outputReserve,"Insufficient liquidity");
        if (isTokenAIn) {
            reserveA+=amountIn;
            reserveB-=amountOut;
        } else {
            reserveB+=amountIn;
            reserveA-=amountOut;
        }
        IERC20(tokenIn).transferFrom(msg.sender,address(this),amountIn);
        IERC20(isTokenAIn?address(tokenB):address(tokenA)).transfer(msg.sender,amountOut);
    }

    function getReserves() external view returns (uint256, uint256) {
        return (reserveA, reserveB);
    }

    function getReserveA() external view returns (uint256) {
        return reserveA;
    }

    function getReserveB() external view returns (uint256) {
        return reserveB;
    }

    function getPriceAinB() external view returns (uint256) {
        require(reserveA>0 && reserveB>0,"Pool is empty");
        return (reserveB*1e18)/reserveA;
    }

    function getPriceBinA() external view returns (uint256) {
        require(reserveA>0 && reserveB>0,"Pool is empty");
        return (reserveA*1e18)/reserveB;
    }

    function getBothPrices()
        external
        view
        returns (uint256 priceAinB, uint256 priceBinA)
    {
        require(reserveA > 0 &&reserveB > 0, "Pool is empty");
        priceAinB=(reserveB * 1e18)/reserveA;
        priceBinA=(reserveA * 1e18)/reserveB;
    }

    function getSpotPrice() external view returns (uint256) {
        require(reserveA>0 && reserveB>0,"Pool is empty");
        return (reserveB * 1e18)/reserveA;
    }

    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x==0) {
            return 0;
        }
        uint256 z=(x+1)/2;
        uint256 y=x;
        while (z<y) {
            y=z;
            z=(x/z+z)/2;
        }
        return y;
    }
}