import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { beforeEach, describe, expect, it } from "vitest";
import { DiscoverWorkspace } from "@/features/discover/discover-workspace";

describe("DiscoverWorkspace", () => {
  beforeEach(() => {
    render(<DiscoverWorkspace />);
  });

  it("renders the approved Discover page and has no basic axe violations", async () => {
    expect(
      screen.getByRole("heading", { name: "Global opportunities" }),
    ).toBeInTheDocument();
    expect(
      screen.getAllByText("Senior Platform Engineer").length,
    ).toBeGreaterThan(0);
    expect((await axe(document.body)).violations).toHaveLength(0);
  });

  it("selects an opportunity and exposes eligibility as text", async () => {
    const user = userEvent.setup();
    await user.click(
      screen.getByRole("button", {
        name: /Developer Experience Engineer at Juniper Works/,
      }),
    );
    expect(
      screen.getByRole("heading", { name: "Developer Experience Engineer" }),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Blocked").length).toBeGreaterThan(0);
  });

  it("searches fixture data", async () => {
    const user = userEvent.setup();
    await user.type(
      screen.getByRole("textbox", { name: "Search opportunities" }),
      "Atlas",
    );
    const filteredList = screen.getByLabelText("1 opportunities");
    expect(
      within(filteredList).getByText("Backend Engineer"),
    ).toBeInTheDocument();
    expect(
      within(filteredList).queryByText("Senior Platform Engineer"),
    ).not.toBeInTheDocument();
  });

  it("saves and unsaves a selected job", async () => {
    const user = userEvent.setup();
    const save = screen.getByRole("button", {
      name: "Save Senior Platform Engineer",
    });
    await user.click(save);
    expect(
      screen.getByRole("button", { name: "Unsave Senior Platform Engineer" }),
    ).toHaveAttribute("aria-pressed", "true");
    await user.click(
      screen.getByRole("button", { name: "Unsave Senior Platform Engineer" }),
    );
    expect(
      screen.getByRole("button", { name: "Save Senior Platform Engineer" }),
    ).toHaveAttribute("aria-pressed", "false");
  });

  it("sorts and filters opportunities", async () => {
    const user = userEvent.setup();
    await user.selectOptions(
      screen.getByRole("combobox", { name: "Sort opportunities" }),
      "capability",
    );
    const list = screen.getByLabelText("4 opportunities");
    const rows = within(list).getAllByRole("article");
    expect(rows[0]).toHaveAccessibleName(/Senior Platform Engineer/);
    await user.selectOptions(
      screen.getByRole("combobox", { name: "Source filter" }),
      "Remotive",
    );
    const remotiveList = screen.getByLabelText("1 opportunities");
    expect(
      within(remotiveList).getByText("Cloud Engineering Intern"),
    ).toBeInTheDocument();
    expect(
      within(remotiveList).queryByText("Backend Engineer"),
    ).not.toBeInTheDocument();
  });

  it("shows insufficient evidence below forty percent", async () => {
    const user = userEvent.setup();
    await user.click(
      screen.getByRole("button", {
        name: /Cloud Engineering Intern at Harbor Research/,
      }),
    );
    expect(screen.getAllByText("Insufficient evidence").length).toBeGreaterThan(
      0,
    );
    expect(
      screen.getByText("Below 40% capability coverage"),
    ).toBeInTheDocument();
  });

  it("preparation never submits and primary controls are keyboard operable", async () => {
    const user = userEvent.setup();
    const action = screen.getByRole("button", { name: "Prepare application" });
    action.focus();
    await user.keyboard("{Enter}");
    expect(
      screen.getAllByText("Preparation does not submit an application.").length,
    ).toBeGreaterThan(0);
  });
});
