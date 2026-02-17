"""
Tests for the learning record service.
"""

import pytest
from uuid import uuid4

from app.models.learning_record import LearningRecordType
from app.services.learning_record_service import LearningRecordService


class TestLearningRecordServiceCreate:
    """Tests for creating learning records."""
    
    def test_create_word_record(self, db_session, test_user):
        """Can create a word learning record."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="hello",
            response_payload={
                "word": "hello",
                "phonetic": "/həˈloʊ/",
                "meaning": "A greeting",
            },
        )
        
        assert record.id is not None
        assert record.user_id == test_user.id
        assert record.input_type == LearningRecordType.word
        assert record.user_input == "hello"
        assert record.response_payload["word"] == "hello"
        assert record.is_favorite == False
        assert record.review_count == 0
    
    def test_create_sentence_record(self, db_session, test_user):
        """Can create a sentence learning record."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.sentence,
            user_input="Hello, how are you?",
            response_payload={
                "sentence": "Hello, how are you?",
                "translation": "你好，你怎么样？",
            },
        )
        
        assert record.input_type == LearningRecordType.sentence
    
    def test_create_topic_record(self, db_session, test_user):
        """Can create a topic learning record."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.topic,
            user_input="Kubernetes",
            response_payload={
                "topic": "Kubernetes",
                "overview": "Container orchestration platform",
            },
        )
        
        assert record.input_type == LearningRecordType.topic
    
    def test_create_record_with_tags(self, db_session, test_user):
        """Can create a record with tags."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="vocabulary",
            response_payload={"word": "vocabulary"},
            tags=["english", "beginner"],
        )
        
        assert record.tags == ["english", "beginner"]
    
    def test_create_record_with_session_id(self, db_session, test_user):
        """Can create a record linked to a session."""
        session_id = uuid4()
        
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="test",
            response_payload={"word": "test"},
            session_id=session_id,
        )
        
        assert record.session_id == session_id


class TestLearningRecordServiceRead:
    """Tests for reading learning records."""
    
    def test_get_record_by_id(self, db_session, test_user):
        """Can get a record by ID."""
        created = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="test",
            response_payload={"word": "test"},
        )
        
        record = LearningRecordService.get_record(
            db=db_session,
            record_id=created.id,
            user_id=test_user.id,
        )
        
        assert record is not None
        assert record.id == created.id
    
    def test_get_record_wrong_user(self, db_session, test_user):
        """Cannot get another user's record."""
        created = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="test",
            response_payload={"word": "test"},
        )
        
        record = LearningRecordService.get_record(
            db=db_session,
            record_id=created.id,
            user_id=999999,  # Different user
        )
        
        assert record is None
    
    def test_list_records(self, db_session, test_user):
        """Can list records with pagination."""
        # Create multiple records
        for i in range(5):
            LearningRecordService.save_learning_record(
                db=db_session,
                user_id=test_user.id,
                input_type=LearningRecordType.word,
                user_input=f"word{i}",
                response_payload={"word": f"word{i}"},
            )
        
        records, total = LearningRecordService.list_learning_records(
            db=db_session,
            user_id=test_user.id,
            limit=3,
            offset=0,
        )
        
        assert len(records) == 3
        assert total >= 5
    
    def test_list_records_by_type(self, db_session, test_user):
        """Can filter records by type."""
        # Create records of different types
        LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="word",
            response_payload={"word": "word"},
        )
        LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.sentence,
            user_input="sentence",
            response_payload={"sentence": "sentence"},
        )
        
        records, total = LearningRecordService.list_learning_records(
            db=db_session,
            user_id=test_user.id,
            type_filter=LearningRecordType.word,
        )
        
        for record in records:
            assert record.input_type == LearningRecordType.word


class TestLearningRecordServiceSearch:
    """Tests for searching learning records."""
    
    def test_search_by_text(self, db_session, test_user):
        """Can search records by text."""
        LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="searchable_unique_word",
            response_payload={"word": "searchable"},
        )
        
        records, total = LearningRecordService.search_learning_records(
            db=db_session,
            user_id=test_user.id,
            query_text="searchable_unique",
        )
        
        assert total >= 1
        assert any("searchable_unique" in r.user_input for r in records)


class TestLearningRecordServiceUpdate:
    """Tests for updating learning records."""
    
    def test_toggle_favorite(self, db_session, test_user):
        """Can toggle favorite status."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="favorite_test",
            response_payload={"word": "favorite"},
        )
        
        assert record.is_favorite == False
        
        # Toggle on
        updated = LearningRecordService.toggle_favorite(
            db=db_session,
            record_id=record.id,
            user_id=test_user.id,
        )
        assert updated.is_favorite == True
        
        # Toggle off
        updated2 = LearningRecordService.toggle_favorite(
            db=db_session,
            record_id=record.id,
            user_id=test_user.id,
        )
        assert updated2.is_favorite == False
    
    def test_mark_reviewed(self, db_session, test_user):
        """Can mark a record as reviewed."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="review_test",
            response_payload={"word": "review"},
        )
        
        assert record.review_count == 0
        assert record.last_reviewed_at is None
        
        updated = LearningRecordService.mark_reviewed(
            db=db_session,
            record_id=record.id,
            user_id=test_user.id,
        )
        
        assert updated.review_count == 1
        assert updated.last_reviewed_at is not None
    
    def test_update_tags(self, db_session, test_user):
        """Can update tags."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="tags_test",
            response_payload={"word": "tags"},
        )
        
        updated = LearningRecordService.update_tags(
            db=db_session,
            record_id=record.id,
            user_id=test_user.id,
            tags=["new", "tags"],
        )
        
        assert updated.tags == ["new", "tags"]


class TestLearningRecordServiceDelete:
    """Tests for deleting learning records."""
    
    def test_soft_delete(self, db_session, test_user):
        """Delete is a soft delete."""
        record = LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="delete_test",
            response_payload={"word": "delete"},
        )
        
        success = LearningRecordService.delete_learning_record(
            db=db_session,
            record_id=record.id,
            user_id=test_user.id,
        )
        
        assert success == True
        
        # Should not be retrievable
        found = LearningRecordService.get_record(
            db=db_session,
            record_id=record.id,
            user_id=test_user.id,
        )
        
        assert found is None


class TestLearningRecordServiceStatistics:
    """Tests for statistics."""
    
    def test_get_statistics(self, db_session, test_user):
        """Can get statistics."""
        # Create some records
        LearningRecordService.save_learning_record(
            db=db_session,
            user_id=test_user.id,
            input_type=LearningRecordType.word,
            user_input="stat1",
            response_payload={"word": "stat1"},
        )
        
        stats = LearningRecordService.get_statistics(
            db=db_session,
            user_id=test_user.id,
        )
        
        assert "total" in stats
        assert "by_type" in stats
        assert "favorites" in stats
        assert "total_reviews" in stats
