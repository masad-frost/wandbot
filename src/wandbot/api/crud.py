from sqlalchemy.orm import Session
from wandbot.api import models, schemas


def create_chat_thread(db: Session, thread_id: str, application: str):
    db_thread = models.ChatThread(thread_id=thread_id, application=application)
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return db_thread


def get_thread(db: Session, thread_id: str):
    return (
        db.query(models.ChatThread)
        .filter(models.ChatThread.thread_id == thread_id)
        .first()
    )


def create_question_answer(db: Session, question_answer: schemas.QuestionAnswerCreate):
    db_question_answer = models.QuestionAnswers(
        question_answer_id=question_answer.question_answer_id,
        thread_id=question_answer.thread_id,
        question=question_answer.question,
        answer=question_answer.answer,
        sources=question_answer.sources,
        start_time=question_answer.start_time,
        end_time=question_answer.end_time,
        time_taken=question_answer.time_taken,
    )
    db.add(db_question_answer)
    db.commit()
    db.refresh(db_question_answer)
    return db_question_answer


def get_question_answer(db: Session, question_answer_id: str, thread_id: str):
    return (
        db.query(models.QuestionAnswers)
        .filter(
            models.QuestionAnswers.question_answer_id == question_answer_id,
            models.QuestionAnswers.thread_id == thread_id,
        )
        .first()
    )


def update_feedback(db: Session, feedback: schemas.FeedbackBase):
    db_question_answer = (
        db.query(models.QuestionAnswers)
        .filter(
            models.QuestionAnswers.question_answer_id == feedback.question_answer_id,
            models.QuestionAnswers.thread_id == feedback.thread_id,
        )
        .first()
    )
    if db_question_answer is None:
        raise ValueError("Question Answer ID not found")
    db_question_answer.feedback = feedback.feedback
    db.commit()
    db.refresh(db_question_answer)
    return db_question_answer