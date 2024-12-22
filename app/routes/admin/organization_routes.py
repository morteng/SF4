@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = OrganizationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            organization_data = {
                'name': form.name.data,
                'description': form.description.data,
                'homepage_url': form.homepage_url.data
            }
            try:
                success, error_message = create_organization(organization_data)
                if success:
                    flash_message(FLASH_MESSAGES["CREATE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                    return redirect(url_for('admin.organization.index'))
                else:
                    flash_message(error_message, FLASH_CATEGORY_ERROR)
                    return redirect(url_for('admin.organization.create'))  # Redirect back to the create page with errors
            except SQLAlchemyError as e:
                db.session.rollback()
                flash_message(FLASH_MESSAGES['CREATE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)
                return redirect(url_for('admin.organization.create'))  # Redirect back to the create page with errors
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash_message(f"{field}: {error}", FLASH_CATEGORY_ERROR)
            flash_message(FLASH_MESSAGES["CREATE_ORGANIZATION_INVALID_FORM"], FLASH_CATEGORY_ERROR)
            return redirect(url_for('admin.organization.create'))  # Redirect back to the create page with errors

    return render_template('admin/organizations/form.html', form=form)

@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        try:
            delete_organization(organization)
            flash_message(FLASH_MESSAGES["DELETE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES['DELETE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)  # Directly use the constant
            return redirect(url_for('admin.organization.index'))
    else:
        flash_message(FLASH_MESSAGES["ORGANIZATION_NOT_FOUND"], FLASH_CATEGORY_ERROR)
    return redirect(url_for('admin.organization.index'))

@admin_org_bp.route('/', methods=['GET'])
@login_required
def index():
    organizations = get_all_organizations()
    return render_template('admin/organizations/index.html', organizations=organizations)

@admin_org_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash_message(FLASH_MESSAGES["ORGANIZATION_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.organization.index'))

    form = OrganizationForm(original_name=organization.name, obj=organization)
    if request.method == 'POST':
        if form.validate_on_submit():
            update_data = {
                'name': form.name.data,
                'description': form.description.data,
                'homepage_url': form.homepage_url.data
            }
            try:
                success, error_message = update_organization(organization, update_data)
                if success:
                    flash_message(FLASH_MESSAGES["UPDATE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                    return redirect(url_for('admin.organization.index'))
                else:
                    flash_message(error_message, FLASH_CATEGORY_ERROR)
                    return redirect(url_for('admin.organization.edit', id=id))  # Redirect back to the edit page with errors
            except SQLAlchemyError as e:
                db.session.rollback()
                flash_message(FLASH_MESSAGES['UPDATE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)  # Directly use the constant
                return redirect(url_for('admin.organization.edit', id=id))  # Redirect back to the edit page with errors
        else:
            # Flash form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash_message(f"{field}: {error}", FLASH_CATEGORY_ERROR)
            flash_message(FLASH_MESSAGES["UPDATE_ORGANIZATION_INVALID_FORM"], FLASH_CATEGORY_ERROR)
            return redirect(url_for('admin.organization.edit', id=id))  # Redirect back to the edit page with errors

    return render_template('admin/organizations/form.html', form=form, organization=organization)
