from flask import Blueprint, render_template, redirect, url_for, flash, request

public_bot_bp = Blueprint('public_bot', __name__, url_prefix='/bots')

# Add your public bot routes here
