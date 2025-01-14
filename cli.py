#!/usr/bin/env python3
import click
import logging
from pathlib import Path
from datetime import datetime
from dicom_manager.models.dicom_data import DicomDataManager
from dicom_manager.models.album import AlbumManager
from dicom_manager.models.query import DicomQuery
from config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

@click.group()
@click.option('--base-dir', default='./DICOM', help='Base directory for DICOM files')
@click.pass_context
def cli(ctx, base_dir):
    """DICOM Album Management CLI"""
    ctx.ensure_object(dict)
    ctx.obj['base_dir'] = base_dir
    ctx.obj['data_manager'] = DicomDataManager(base_dir)
    ctx.obj['album_manager'] = AlbumManager(base_dir)
    ctx.obj['query'] = DicomQuery(ctx.obj['data_manager'])

@cli.command()
@click.pass_context
@click.argument('directory')
def scan(ctx, directory):
    """Scan a directory for DICOM files"""
    count = ctx.obj['data_manager'].scan_directory(directory)
    click.echo(f"Processed {count} DICOM files")

@cli.command()
@click.pass_context
@click.option('--name', required=True, help='Album name')
@click.option('--description', help='Album description')
def create_album(ctx, name, description):
    """Create a new album"""
    album = ctx.obj['album_manager'].create_album(name, description)
    click.echo(f"Created album '{name}' with ID: {album.album_id}")

@cli.command()
@click.pass_context
@click.argument('album_id')
@click.argument('image_paths', nargs=-1)
def add_images(ctx, album_id, image_paths):
    """Add images to an album"""
    success = ctx.obj['album_manager'].add_images_to_album(album_id, image_paths)
    if success:
        click.echo(f"Added {len(image_paths)} images to album {album_id}")
    else:
        click.echo("Failed to add images")

@cli.command()
@click.pass_context
def list_albums(ctx):
    """List all albums"""
    albums = ctx.obj['album_manager'].list_albums()
    for album in albums:
        click.echo(f"\nAlbum: {album.name} ({album.album_id})")
        click.echo(f"Description: {album.description}")
        click.echo(f"Images: {len(album.images)}")
        click.echo(f"Created: {album.created_at}")

@cli.group()
def query():
    """Query DICOM data"""
    pass

@query.command()
@click.pass_context
@click.option('--patient-id', help='Patient ID to search for')
@click.option('--patient-name', help='Patient name to search for')
def by_patient(ctx, patient_id, patient_name):
    """Query by patient information"""
    results = ctx.obj['query'].query_by_metadata(patient_id, patient_name)
    for patient in results:
        click.echo(f"\nPatient ID: {patient.patient_id}")
        click.echo(f"Patient Name: {patient.patient_name}")
        click.echo(f"Studies: {len(patient.studies)}")

@query.command()
@click.pass_context
@click.option('--date-from', help='Study date from (YYYY-MM-DD)')
@click.option('--date-to', help='Study date to (YYYY-MM-DD)')
@click.option('--description', help='Study description')
def by_study(ctx, date_from, date_to, description):
    """Query by study information"""
    date_from = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    results = ctx.obj['query'].query_by_study(date_from, date_to, description)
    for study in results:
        click.echo(f"\nStudy UID: {study.study_instance_uid}")
        click.echo(f"Description: {study.study_description}")
        click.echo(f"Date: {study.study_date}")
        click.echo(f"Series: {len(study.series)}")

@query.command()
@click.pass_context
@click.option('--modality', help='Modality (CT, MR, etc.)')
@click.option('--series-number', type=int, help='Series number')
@click.option('--description', help='Series description')
def by_series(ctx, modality, series_number, description):
    """Query by series information"""
    results = ctx.obj['query'].query_by_series(modality, series_number, description)
    for series in results:
        click.echo(f"\nSeries UID: {series.series_instance_uid}")
        click.echo(f"Modality: {series.modality}")
        click.echo(f"Description: {series.series_description}")
        click.echo(f"Images: {len(series.images)}")

@cli.command()
@click.pass_context
@click.option('--album-name', required=True, help='Name for the new album')
@click.option('--query-type', type=click.Choice(['patient', 'study', 'series']), required=True)
@click.option('--patient-id', help='Patient ID for patient query')
@click.option('--modality', help='Modality for series query')
@click.option('--study-description', help='Study description for study query')
def create_from_query(ctx, album_name, query_type, patient_id, modality, study_description):
    """Create album from query results"""
    query_params = {}
    
    if query_type == 'patient' and patient_id:
        query_params['patient_id'] = patient_id
    elif query_type == 'series' and modality:
        query_params['modality'] = modality
    elif query_type == 'study' and study_description:
        query_params['description'] = study_description
    
    album_id = ctx.obj['query'].create_album_from_query(
        ctx.obj['album_manager'],
        album_name,
        query_type,
        query_params
    )
    
    click.echo(f"Created album '{album_name}' with ID: {album_id}")

if __name__ == '__main__':
    cli(obj={})