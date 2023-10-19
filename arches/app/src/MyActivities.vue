<template>
    <div class="my-activities-container">
        <div class="component-title">My Activities</div>
        <div class="activities-tiles-container">
            <div class="tile-row">
                <div class="tile new-resources">
                    <div class="activity-count">138k</div>
                    <div class="activity-type">Resources Created</div>
                </div>
                <div class="tile edited-resources">
                    <div class="activity-count">164</div>
                    <div class="activity-type">Resources Edited</div>
                </div>
            </div>
            <div class="tile-row">
                <div class="tile workflows-completed">
                    <div class="activity-count">7</div>
                    <div class="activity-type">Workflows Completed</div>
                </div>
                <div class="tile etl-jobs-initiated">
                    <div class="activity-count">16</div>
                    <div class="activity-type">ETL Jobs Intiated</div>
                </div>
            </div>    
        </div>
    </div>
</template>

<style scoped>
    .my-activities-container {
        padding: 10px 10px 10px 20px;
        font-family: 'Open Sans','Helvetica Neue',Helvetica,Arial,sans-serif;
    }

    .component-title {
        font-size: 19px;
        color: #565656;
        padding: 5px;
    }

    .tile-row {
        display: flex;
        flex-direction: row;
        margin-bottom: 5px;
    }

    .tile {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        width: 125px;
        height: 170px;
        margin-right: 5px;
        text-align: center;
        color: #f2f2f2;
        border-radius: 3px;
    }

    .tile.new-resources {
        background: #1E6B8B;
    }

    .tile.edited-resources {
        background: #2B3A97;
    }

    .tile.workflows-completed {
        background: #DDA927;
    }

    .tile.etl-jobs-initiated {
        background: #DD8727;
    }

    .activity-count {
        font-size: 48px;
        padding-top: 20px;
        font-weight: 200;
    }

    .activity-type {
        font-size: 15px;
        padding: 10px 10px 15px 10px;
        font-weight: 300;
    }
</style>