import reflex as rx
import dill
import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

with open("text_suggestion_em.pkl", "rb") as file:
    text_suggestion = dill.load(file)

logger.info("Text Suggestion was readen")

with open("tokenizer.pkl", "rb") as file:
    tokenizer = dill.load(file)

logger.info("Tokenizer was readen")

class MailState(rx.State):
    email: str = ""
    subject: str = ""
    body: str = ""
    suggestion: str = ""
    suggestions: list[str] = []

    def send_mail(self):
        if not self.email or not self.subject or not self.body:
            self.suggestion = "Все поля должны быть заполнены!"
        else:
            self.suggestion = "Письмо отправлено."

    def update_suggestions(self, text: str):
        self.body = text
        if text and len(text.split()) >= 2:
            tokens = tokenizer.encode(text).tokens[:-1]
            suggestion = text_suggestion.suggest_text(tokens)[0][1:]
            if suggestion == ["[EOS]", "[EOS]", "[EOS]"]:
                self.suggestion = []
            else:
                self.suggestions = [" ".join(suggestion)]
        else:
            self.suggestions = []

    def choose_suggestion(self, suggestion: str):
        self.body += " " + suggestion
        self.suggestions = []

def mail_form():
    return rx.vstack(
        rx.heading("AUMail", size="lg", align='center'),

        rx.input(
            value=MailState.email,
            placeholder="Введите email получателя...",
            on_change=MailState.set_email,
            width="300px",
            height="50px",
        ),

        rx.input(
            value=MailState.subject,
            placeholder="Введите тему письма...",
            on_change=MailState.set_subject,
            width="300px",
            height="50px",
        ),

        rx.text_area(
            value=MailState.body,
            placeholder="Введите текст письма...",
            on_change=MailState.update_suggestions,
            width="300px",
            height="300px",
        ),

        rx.cond(
            MailState.suggestions != [],
            rx.foreach(
                MailState.suggestions,
                lambda suggestion: rx.text(
                    suggestion,
                    color="white",
                    cursor="pointer",
                    on_click=lambda s=suggestion: MailState.choose_suggestion(s),
                )
            )
        ),

        rx.button(
            "Отправить",
            on_click=MailState.send_mail,
        ),

        rx.cond(
            MailState.suggestion.contains("Письмо отправлено"), 
            rx.text(MailState.suggestion, color="green"),
            rx.text(MailState.suggestion, color="red"),
        ),

        spacing="20px",
    )

app = rx.App()
app.add_page(mail_form, route="/")
