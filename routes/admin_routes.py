from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.database_models import User, Document, DocumentAnalysis, Conversation, Message, KnowledgeBase
from utils import admin_required
from services.embedding_service import index_kb_entry, delete_kb_vectors

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _get_admin_dashboard_context(tab='stats'):
    total_users          = User.query.count()
    total_documents      = Document.query.count()
    total_analyses       = DocumentAnalysis.query.count()
    total_conversations  = Conversation.query.count()
    total_messages       = Message.query.count()
    total_kb_entries     = KnowledgeBase.query.count()

    recent_registrations = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_documents     = Document.query.order_by(Document.uploaded_at.desc()).limit(5).all()
    recent_conversations = Conversation.query.order_by(Conversation.updated_at.desc()).limit(5).all()
    kb_entries           = KnowledgeBase.query.all()
    users                = User.query.order_by(User.created_at.desc()).all()

    return {
        'total_users': total_users,
        'total_documents': total_documents,
        'total_analyses': total_analyses,
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'total_kb_entries': total_kb_entries,
        'recent_registrations': recent_registrations,
        'recent_documents': recent_documents,
        'recent_conversations': recent_conversations,
        'kb_entries': kb_entries,
        'users': users,
        'tab': tab
    }


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    tab = request.args.get('tab', 'stats')
    context = _get_admin_dashboard_context(tab=tab)
    return render_template('admin.html', **context)


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    if request.is_json or request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'created_at': u.created_at.strftime('%Y-%m-%d') if u.created_at else None
        } for u in users])
    context = _get_admin_dashboard_context(tab='users')
    return render_template('admin.html', **context)


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    new_role = request.form.get('role')

    if new_role not in ['user', 'admin']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('admin.dashboard', tab='users'))

    if user.role == 'admin' and new_role == 'user':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot demote the last remaining admin.', 'danger')
            return redirect(url_for('admin.dashboard', tab='users'))

    user.role = new_role
    db.session.commit()
    flash(f"User {user.email}'s role updated to {new_role}.", 'success')
    return redirect(url_for('admin.dashboard', tab='users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    if user.id == current_user.id:
        flash('You cannot delete your own logged-in account.', 'danger')
        return redirect(url_for('admin.dashboard', tab='users'))

    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot delete the last remaining admin.', 'danger')
            return redirect(url_for('admin.dashboard', tab='users'))

    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.email} has been deleted successfully.", 'success')
    return redirect(url_for('admin.dashboard', tab='users'))


@admin_bp.route('/kb/add', methods=['POST'])
@login_required
@admin_required
def kb_add():
    title    = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    content  = request.form.get('content', '').strip()
    source   = request.form.get('source', '').strip() or None

    if not title or not category or not content:
        flash('Title, category, and content are mandatory.', 'danger')
        return redirect(url_for('admin.dashboard', tab='kb'))

    if len(title) > 255:
        flash('Title cannot exceed 255 characters.', 'danger')
        return redirect(url_for('admin.dashboard', tab='kb'))

    if len(content) > 50000:
        flash('Content exceeds maximum allowed size (50,000 characters).', 'danger')
        return redirect(url_for('admin.dashboard', tab='kb'))

    new_kb = KnowledgeBase(
        title=title, category=category, content=content,
        source=source, created_by=current_user.id
    )
    db.session.add(new_kb)
    db.session.commit()

    success = index_kb_entry(new_kb.id, title, category, content, source)
    
    if success:
        flash('Knowledge Base entry added and indexed successfully.', 'success')
    else:
        flash('Entry saved to database, but ChromaDB indexing failed.', 'warning')

    return redirect(url_for('admin.dashboard', tab='kb'))


@admin_bp.route('/kb/edit/<int:kb_id>', methods=['POST'])
@login_required
@admin_required
def kb_edit(kb_id):
    kb = db.session.get(KnowledgeBase, kb_id)
    if kb is None:
        abort(404)
    title    = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    content  = request.form.get('content', '').strip()
    source   = request.form.get('source', '').strip() or None

    if not title or not category or not content:
        flash('Title, category, and content are mandatory.', 'danger')
        return redirect(url_for('admin.dashboard', tab='kb'))

    if len(title) > 255:
        flash('Title cannot exceed 255 characters.', 'danger')
        return redirect(url_for('admin.dashboard', tab='kb'))

    if len(content) > 50000:
        flash('Content exceeds maximum allowed size.', 'danger')
        return redirect(url_for('admin.dashboard', tab='kb'))

    kb.title    = title
    kb.category = category
    kb.content  = content
    kb.source   = source
    db.session.commit()

    delete_kb_vectors(kb.id)
    index_kb_entry(kb.id, title, category, content, source)

    flash('Knowledge Base entry updated successfully.', 'success')
    return redirect(url_for('admin.dashboard', tab='kb'))


@admin_bp.route('/kb/delete/<int:kb_id>', methods=['POST'])
@login_required
@admin_required
def kb_delete(kb_id):
    kb = db.session.get(KnowledgeBase, kb_id)
    if kb is None:
        abort(404)

    delete_kb_vectors(kb.id)
    db.session.delete(kb)
    db.session.commit()

    flash('Knowledge Base entry deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard', tab='kb'))
