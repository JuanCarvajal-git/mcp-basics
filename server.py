from mcp.server.mcpserver import MCPServer

# The name here is just an identifier the client will show the user.
mcp = MCPServer("my-first-server")

@mcp.tool()
async def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"
 
@mcp.tool()
async def add(a: float, b: float) -> str:
    """Add two numbers together."""
    return str(a + b)
 
 
@mcp.tool()
async def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]
 
 
@mcp.tool()
async def word_count(text: str) -> str:
    """Count the number of words in a piece of text."""
    count = len(text.split())
    return f"{count} word{'s' if count != 1 else ''}"
 
 
@mcp.tool()
async def is_prime(n: int) -> str:
    """Check whether a number is prime."""
    if n < 2:
        return f"{n} is not prime."
    for divisor in range(2, int(n ** 0.5) + 1):
        if n % divisor == 0:
            return f"{n} is not prime (divisible by {divisor})."
    return f"{n} is prime."


if __name__ == "__main__":
    mcp.run()
