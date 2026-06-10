const hre = require("hardhat");

async function main() {
  const BLAI = await hre.ethers.deployContract("BLAI");
  await BLAI.waitForDeployment();
  console.log("BLAI deployed to:", await BLAI.getAddress());
}

main().catch(console.error);
