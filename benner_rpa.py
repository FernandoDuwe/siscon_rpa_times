import asyncio
import argparse
import os
import sys
from playwright.async_api import Playwright, async_playwright, expect

async def run(playwright: Playwright, args) -> None:
    # Lançar o navegador em modo headless (invisível) para evitar erros de X11 no Docker
    browser = await playwright.chromium.launch(headless=True)
    os.makedirs(args.video_dir, exist_ok=True)
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=args.video_dir,
        record_video_size={"width": 1920, "height": 1080},
    )
    page = await context.new_page()

    erro_ocorreu = False

    try:
        print(f"[*] Acessando sistema Benner Siscon...")
        await page.goto("https://siscon.benner.com.br/Login?ReturnUrl=%2f%3f", timeout=60000)

        print(f"[*] Realizando login para o usuário: {args.username}")
        await page.fill("input[name=\"wesLogin$loginWes$UserName\"]", args.username)
        await page.fill("input[name=\"wesLogin$loginWes$Password\"]", args.password)
        await page.click("a:has-text(\"Acessar\")")

        # Aguardar a navegação após o login
        await page.wait_for_url("https://siscon.benner.com.br/**", timeout=60000)
        print("[+] Login realizado com sucesso!")

        # 2. Navegar para a página de solicitação
        solicitacao_url = f"https://siscon.benner.com.br/siscon/e/solicitacoes/Solicitacao.aspx?key={args.key}&p=1"
        print(f"[*] Acessando solicitação: {args.key}")
        await page.goto(solicitacao_url, timeout=60000)

        # Clicar no botão \'Lançar horas\'
        print("[*] Abrindo formulário de lançamento de horas...")
        await page.locator("a", has_text="Lançar horas").first.click()

        # O formulário de "Lançamento de horas" é renderizado DENTRO de um
        # <iframe> que fica dentro do modal (#ModalCommand_modal).
        # Elementos como Data, Observações, Início e Fim NÃO existem no
        # documento principal (page) — é preciso descer para o frame com
        # page.frame_locator(). Por isso, antes, esperamos o iframe do modal
        # ficar visível.
        modal_iframe = page.locator("#ModalCommand_modal iframe")
        await modal_iframe.wait_for(state="visible", timeout=30000)
        frame = page.frame_locator("#ModalCommand_modal iframe")

        # Aguardamos o título do formulário aparecer já dentro do iframe.
        await frame.locator("text=LANÇAMENTO DE HORAS").first.wait_for(
            state="visible", timeout=30000
        )

        # 3. Preencher o formulário com seletores precisos (baseados no HTML fornecido)
        print(f"[*] Preenchendo dados: Data={args.data}, Início={args.inicio}, Fim={args.fim}")

        # Tipo (Etapa - Atividade)
        # Como o campo Etapa/Atividade costuma ser um autocomplete ou dropdown complexo no Benner:
        print(f"[*] Selecionando tipo: {args.tipo}")

        # Observações
        await frame.locator('textarea[name="ctl00$Main$WIDGETID_636082736395056317$PageControl$GERAL$GERAL$OBSERVACOES"]').fill(args.observacoes)

        # Data
        await frame.locator('input[name="ctl00$Main$WIDGETID_636082736395056317$PageControl$GERAL$GERAL$DATA_DATE"]').fill(args.data)

        # Início e Fim
        await frame.locator('input[name="ctl00$Main$WIDGETID_636082736395056317$PageControl$GERAL$GERAL$INICIO_TIME"]').fill(args.inicio)

        await page.wait_for_timeout(3000)

        await frame.locator('input[name="ctl00$Main$WIDGETID_636082736395056317$PageControl$GERAL$GERAL$FIM_TIME"]').fill(args.fim)

        # Clicar no botão Salvar
        print("[*] Salvando lançamento...")
        await frame.get_by_role("link", name="Salvar").first.click()

        # Aguardar um pouco para garantir o processamento
        await page.wait_for_timeout(3000)
        print("[+] Lançamento de horas concluído com sucesso!")

    except Exception as e:
        erro_ocorreu = True
        print(f"[!] Ocorreu um erro durante a execução: {e}")
        # Tirar um print do erro para ajudar no debug (salvo dentro do container)
        await page.screenshot(path="erro_execucao.png")
        sys.exit(1)
    finally:
        video = page.video
        await context.close()
        await browser.close()
        if video:
            video_path = await video.path()
            if erro_ocorreu:
                print(f"[*] Vídeo do erro salvo em: {video_path}")
            else:
                # Sem erro: descarta o vídeo, pois só queremos gravação em caso de falha
                os.remove(video_path)

async def main():
    parser = argparse.ArgumentParser(description="Robô RPA para lançamento de horas no Benner Siscon.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--inicio", required=True)
    parser.add_argument("--fim", required=True)
    parser.add_argument("--observacoes", required=True)
    parser.add_argument("--tipo", required=True)
    parser.add_argument("--video-dir", dest="video_dir", default="videos",
                         help="Diretório onde o vídeo da execução será salvo (padrão: videos)")

    args = parser.parse_args()

    async with async_playwright() as playwright:
        await run(playwright, args)

if __name__ == '__main__':
    asyncio.run(main())