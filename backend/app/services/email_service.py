from email.message import EmailMessage
from email.utils import formataddr
from html import escape
import smtplib
from urllib.parse import urlencode

from backend.app.core.config import settings


class EmailConfigurationError(RuntimeError):
    pass


def _verification_url(email: str, token: str) -> str:
    query = urlencode({"email": email, "token": token})
    return f"{settings.APP_URL.rstrip('/')}/verificar.html?{query}"


def enviar_email_verificacao(destinatario: str, nome: str, token: str) -> bool:
    """Envia a confirmação por SMTP. Retorna False somente no modo de desenvolvimento."""
    if settings.EMAIL_DEV_MODE:
        return False
    if not all((settings.SMTP_HOST, settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.SMTP_FROM_EMAIL)):
        raise EmailConfigurationError("O envio de e-mail ainda não foi configurado no servidor.")

    link = _verification_url(destinatario, token)
    nome_seguro = escape(nome)
    mensagem = EmailMessage()
    mensagem["Subject"] = "Confirme seu e-mail na Nexora"
    mensagem["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
    mensagem["To"] = destinatario
    mensagem.set_content(f"Olá, {nome}. Confirme seu e-mail por este link, válido por 24 horas: {link}")
    mensagem.add_alternative(
        f"""<!doctype html><html><body style="margin:0;background:#080b14;font-family:Arial,sans-serif;color:#f5f7ff">
        <div style="max-width:560px;margin:0 auto;padding:42px 22px"><div style="background:#111625;border:1px solid #292d3e;border-radius:20px;padding:34px">
        <div style="font-weight:800;color:#9d8cff;letter-spacing:2px">NEXORA</div><h1 style="font-size:25px;margin:28px 0 10px">Confirme seu e-mail</h1>
        <p style="color:#a1a9bc;line-height:1.65">Olá, {nome_seguro}. Clique no botão abaixo para confirmar que este endereço pertence a você.</p>
        <a href="{escape(link, quote=True)}" style="display:inline-block;margin:18px 0;padding:14px 22px;border-radius:11px;background:#715cff;color:white;text-decoration:none;font-weight:bold">Verificar meu e-mail</a>
        <p style="color:#687188;font-size:12px;line-height:1.6">O link expira em 24 horas. Se você não criou esta conta, ignore esta mensagem.</p>
        </div></div></body></html>""", subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as servidor:
        if settings.SMTP_USE_TLS:
            servidor.starttls()
        servidor.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        servidor.send_message(mensagem)
    return True


def enviar_email_recuperacao(destinatario: str, nome: str, token: str) -> bool:
    """Envia um link de redefinição de senha sem expor o token na API."""
    if settings.EMAIL_DEV_MODE:
        return False
    if not all((settings.SMTP_HOST, settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.SMTP_FROM_EMAIL)):
        raise EmailConfigurationError("O envio de e-mail ainda não foi configurado no servidor.")

    query = urlencode({"token": token})
    link = f"{settings.APP_URL.rstrip('/')}/recuperar.html?{query}"
    nome_seguro = escape(nome)
    mensagem = EmailMessage()
    mensagem["Subject"] = "Redefina sua senha na Nexora"
    mensagem["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
    mensagem["To"] = destinatario
    mensagem.set_content(f"Olá, {nome}. Redefina sua senha por este link, válido por 30 minutos: {link}")
    mensagem.add_alternative(
        f"""<!doctype html><html><body style="margin:0;background:#080b14;font-family:Arial,sans-serif;color:#f5f7ff">
        <div style="max-width:560px;margin:0 auto;padding:42px 22px"><div style="background:#111625;border:1px solid #292d3e;border-radius:20px;padding:34px">
        <div style="font-weight:800;color:#9d8cff;letter-spacing:2px">NEXORA</div><h1 style="font-size:25px;margin:28px 0 10px">Redefina sua senha</h1>
        <p style="color:#a1a9bc;line-height:1.65">Olá, {nome_seguro}. Recebemos uma solicitação para alterar sua senha.</p>
        <a href="{escape(link, quote=True)}" style="display:inline-block;margin:18px 0;padding:14px 22px;border-radius:11px;background:#715cff;color:white;text-decoration:none;font-weight:bold">Criar nova senha</a>
        <p style="color:#687188;font-size:12px;line-height:1.6">O link expira em 30 minutos. Se não foi você, ignore esta mensagem.</p>
        </div></div></body></html>""", subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as servidor:
        if settings.SMTP_USE_TLS:
            servidor.starttls()
        servidor.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        servidor.send_message(mensagem)
    return True
