import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from argparse import ArgumentParser

## parameters
font_size = 25
step_per_frame = 10
fig_width = 20
fig_height = 15
cmap_style = "RdYlGn"
time_coloumn = "time"
id_coloumn = "vehicle_id"
yaw_coloume = "rotation_yaw"
loc_x = "location_x"
loc_y = "location_y"
time_spot_font_size = 20
time_spot_size = 5


# Function to calculate velocity magnitude for color mapping
# !!! Modify this function to calculate the velocity magnitude
def calculate_velocity(row):
    return (
        np.sqrt(
            row["velocity_x"] ** 2 + row["velocity_y"] ** 2 + row["velocity_z"] ** 2
        )
        ** 2
    )


def draw_vehicle(ax, x, y, yaw, color="blue"):
    width, length = 2.5, 4.0  # Vehicle dimensions

    # Calculate the rectangle's bottom-left corner (before rotation)
    # Assuming x, y is the center; we offset by half the width/length to get the bottom-left corner
    bottom_left_x = x - length / 2
    bottom_left_y = y - width / 2

    # Create the rectangle
    rect = patches.Rectangle(
        (bottom_left_x, bottom_left_y),
        length,
        width,
        linewidth=2,
        edgecolor=color,
        facecolor="none",
        zorder=10,
    )

    # Apply rotation about the center of the rectangle
    # Matplotlib's rotate_around takes the point to rotate around (x, y here) and the angle in degrees
    rect.set_transform(
        patches.transforms.Affine2D().rotate_around(x, y, np.deg2rad(yaw))
        + ax.transData
    )

    ax.add_patch(rect)


def main():
    arg = ArgumentParser()
    arg.add_argument("--file", type=str, default="data/data0.csv")

    file_name = arg.parse_args().file
    data = pd.read_csv(file_name)
    data["velocity"] = data.apply(calculate_velocity, axis=1)
    # Add velocity magnitude to the dataframe

    # Normalize velocity magnitude for color mapping (0-1)
    max_velocity = data["velocity"].max()
    min_velocity = data["velocity"].min()
    data["velocity_normalized"] = (data["velocity"] - min_velocity) / (
        max_velocity - min_velocity
    )
    plt.rcParams.update({"font.size": font_size})

    # Plotting
    unique_times = data[time_coloumn].unique()
    for i in range(0, len(unique_times), step_per_frame):
        fig, ax = plt.subplots()
        fig.set_size_inches(fig_width, fig_height)
        fig.set_dpi(300)
        subset = data[
            data[time_coloumn]
            <= unique_times[min(i + step_per_frame - 1, len(unique_times) - 1)]
        ]
        norm = mcolors.Normalize(vmin=min_velocity, vmax=max_velocity)
        sm = cm.ScalarMappable(norm=norm, cmap=cmap_style)

        for vehicle_id in subset[id_coloumn].unique():
            vehicle_data = subset[subset[id_coloumn] == vehicle_id].sort_values(
                by=time_coloumn
            )
            color_values = vehicle_data["velocity_normalized"]

            # Plot line segments with color based on speed
            for j in range(1, len(vehicle_data)):
                x = vehicle_data.iloc[j - 1 : j + 1][loc_x].values
                y = vehicle_data.iloc[j - 1 : j + 1][loc_y].values
                vel_norm = color_values.iloc[j - 1 : j + 1].mean()
                ax.plot(x, y, color=plt.cm.RdYlGn(vel_norm), linewidth=5)

            # Add time texts every 10 steps
            for k in range(0, len(vehicle_data), 10):
                if k < len(vehicle_data):
                    row = vehicle_data.iloc[k]
                    ax.text(
                        row[loc_x] + 1,
                        row[loc_y] + 1,
                        f"{int(k/10)}s",
                        color="black",
                        fontsize=time_spot_font_size,
                    )
                    ax.plot(
                        row[loc_x],
                        row[loc_y],
                        "o",
                        color="black",
                        markersize=time_spot_size,
                    )

            # Draw the last position of the vehicle as a box
            last_row = vehicle_data.iloc[-1]
            draw_vehicle(
                ax,
                last_row[loc_x],
                last_row[loc_y],
                last_row[yaw_coloume],
            )

        ax.set_xlabel("Location X (m)")
        ax.set_ylabel("Location Y (m)")
        ax.set_title(
            f"Time of {int(min(i+step_per_frame, len(unique_times))/10)}s tranjectory"
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label("Speed (m/s)")
        plt.axis("equal")
        file_name_middle = file_name.split("/")[-1].split(".")[0]
        plt.savefig(f"res/{file_name_middle}_t_{int(i/10)+1}.png", transparent=True)
        print(f"{file_name_middle}_t_{int(i/10)+1}.png is saved")


if __name__ == "__main__":
    main()
