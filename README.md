# Pokemon
## WSL 알아보기

- ubuntu 설치
```bash
wsl --install ubuntu
```

- 가상화 목록
```bash
wsl -l -v
```

- Ubuntu 재접속(WSL)
```bash
wsl -d Ubuntu
```

- Ubuntu 데이터 삭제
```bash
wsl --unregister Ubuntu
```

## Ubuntu 설정

- package 설치
```bash
sudo apt update && sudo apt -y upgrade
```

- python 설치
```bash
sudo apt install -y git python3 python3-venv python3-pip
```

- python 버젼 확인
```bash
python3 --version
```

## Hugginface 

- 인증 (로그인)
```bash
huggingface-cli login
```

---

- [token 생성](https://huggingface.co/settings/tokens)
```bash
export HF_TOKEN="토큰_값"
```

## VLLM 설정

- 작업 공간(폴더) 만들기
```bash
mkdir -p ~/ai/vllm
cd ~/ai/vllm
```

- python 가상화(격리화) 구성하기
```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Huggingface hub 설치
```bash
pip install -U "huggingface_hub"
```

- GPU 확인
```bash
nvidia-smi
```

- python 표준 바이너리 배포 포멧 설치
```bash
python -m pip install -U pip wheel
```

- vllm 설치
```bash
pip install -U vllm
```

- python package 목록 확인
```bash
pip list
```

- vllm 설치 확인
```bash
python -c "import vllm; print(vllm.__version__)"
```

- vllm 명령어 확인
```bash
vllm --help
```

- VLLM 서버 실행
```bash
vllm serve \
kakaocorp/kanana-nano-2.1b-base \
--gpu-memory-utilization 0.8 
```

- VLLM 모델 확인
```bash
ls -l ~/.cache/huggingface/hub/
```

- GPU 사용량 확인
```bash
nvidia-smi dmon -s pucm
```

- CURL 사용
```bash
# Call the server using curl (OpenAI-compatible API):
curl -X POST "http://127.0.0.1:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "kakaocorp/kanana-nano-2.1b-base",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'
```
