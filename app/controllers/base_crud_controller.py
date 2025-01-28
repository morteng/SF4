from flask import render_template, redirect, url_for
from app.utils import admin_required
from app.extensions import db

class BaseCrudController:
    def __init__(self, service, entity_name, form_class, template_dir):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class
        self.template_dir = template_dir

    def create(self):
        form = self.form_class()
        if form.validate_on_submit():
            try:
                self.service.create(form.data)
                return redirect(url_for(f'{self.template_dir}.index'))
            except Exception as e:
                db.session.rollback()
                return render_template(f'{self.template_dir}/create.html', form=form), 400
        return render_template(f'{self.template_dir}/create.html', form=form)

    def edit(self, id):
        entity = self.service.get(id)
        form = self.form_class(obj=entity)
        if form.validate_on_submit():
            try:
                self.service.update(id, form.data)
                return redirect(url_for(f'{self.template_dir}.index'))
            except Exception as e:
                db.session.rollback()
                return render_template(f'{self.template_dir}/edit.html', form=form), 400
        return render_template(f'{self.template_dir}/edit.html', form=form)

    def delete(self, id):
        try:
            self.service.delete(id)
            return redirect(url_for(f'{self.template_dir}.index'))
        except Exception as e:
            db.session.rollback()
            return redirect(url_for(f'{self.template_dir}.index'))

    def index(self):
        entities = self.service.get_all()
        return render_template(f'{self.template_dir}/index.html', entities=entities)
