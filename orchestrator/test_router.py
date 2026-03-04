from model_router import ModelRouter

router = ModelRouter()

response = router.generate(
    role="planner",
    prompt="Explain AI agents in one sentence"
)

print(response)